from ui.xray_config_builder import build_xray_config


class TestBuildXrayConfig:
    def test_single_vless_config(self, sample_config):
        result = build_xray_config([sample_config])
        assert "inbounds" in result
        assert len(result["inbounds"]) == 3  # ws + tls + api

        ws_inbounds = [i for i in result["inbounds"] if "ws-" in i["tag"] and "tls" not in i["tag"]]
        tls_inbounds = [i for i in result["inbounds"] if "ws-tls" in i["tag"]]
        assert len(ws_inbounds) == 1
        assert len(tls_inbounds) == 1

        ws = ws_inbounds[0]
        assert ws["port"] == 8080
        assert ws["protocol"] == "vless"
        assert ws["streamSettings"]["network"] == "ws"

        tls = tls_inbounds[0]
        assert tls["port"] == 8443
        assert tls["streamSettings"]["security"] == "tls"
        assert "tlsSettings" in tls["streamSettings"]

    def test_vmess_config(self, sample_config_vmess):
        result = build_xray_config([sample_config_vmess])
        ws_inbounds = [i for i in result["inbounds"] if "ws-" in i["tag"] and "tls" not in i["tag"]]
        clients = ws_inbounds[0]["settings"]["clients"]
        assert clients[0].get("alterId") == 0

    def test_ws_only_config(self, sample_config_ws_only):
        result = build_xray_config([sample_config_ws_only])
        tls_inbounds = [i for i in result["inbounds"] if "ws-tls" in i["tag"]]
        assert len(tls_inbounds) == 0

    def test_tls_only_config(self, sample_config_tls_only):
        result = build_xray_config([sample_config_tls_only])
        tls_inbounds = [i for i in result["inbounds"] if i["tag"].startswith("ws-tls-")]
        assert len(tls_inbounds) == 1

    def test_disabled_config_skipped(self, sample_config):
        sample_config["enabled"] = False
        result = build_xray_config([sample_config])
        ws_inbounds = [i for i in result["inbounds"] if "ws-" in i["tag"] and "tls" not in i["tag"]]
        assert len(ws_inbounds) == 0

    def test_multiple_configs(self, sample_config, sample_config_vmess):
        result = build_xray_config([sample_config, sample_config_vmess])
        ws_inbounds = [i for i in result["inbounds"] if "ws-" in i["tag"] and "tls" not in i["tag"]]
        assert len(ws_inbounds) == 2

    def test_api_inbound_always_present(self, sample_config):
        result = build_xray_config([sample_config])
        api_inbounds = [i for i in result["inbounds"] if i["tag"] == "api"]
        assert len(api_inbounds) == 1
        assert api_inbounds[0]["port"] == 10085

    def test_outbounds_and_routing(self, sample_config):
        result = build_xray_config([sample_config])
        assert len(result["outbounds"]) == 2
        assert result["outbounds"][0]["protocol"] == "freedom"
        assert result["routing"]["domainStrategy"] == "IPOnDemand"

    def test_log_config(self, sample_config):
        result = build_xray_config([sample_config])
        assert result["log"]["loglevel"] == "info"
        assert "access" in result["log"]

    def test_stats_and_policy(self, sample_config):
        result = build_xray_config([sample_config])
        assert result["stats"] == {}
        assert "StatsService" in result["api"]["services"]
        assert result["policy"]["levels"]["0"]["statsUserUplink"] is True

    def test_dns_from_first_config(self, sample_config, sample_config_vmess):
        sample_config["dns"] = "8.8.8.8"
        sample_config_vmess["dns"] = "1.1.1.1"
        result = build_xray_config([sample_config, sample_config_vmess])
        assert result["dns"]["servers"][0]["address"] == "8.8.8.8"

    def test_empty_configs_list(self):
        result = build_xray_config([])
        assert len(result["inbounds"]) == 1  # only the API inbound
        assert result["inbounds"][0]["tag"] == "api"
