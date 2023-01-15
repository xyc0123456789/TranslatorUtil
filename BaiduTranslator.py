import traceback

import execjs
import requests


class BaiduTranslateJS(object):
    def __init__(self):
        """

        :param query: 待翻译的内容
        cookie 值 可能会影响到翻译结果，可以将未登陆情况下百度翻译的cookie填写。
        """
        self.ctx = execjs.compile(r'''
function e(t, e) {
    (null == e || e > t.length) && (e = t.length);
    for (var n = 0, r = new Array(e); n < e; n++)
        r[n] = t[n];
    return r
}
function n(t, e) {
    for (var n = 0; n < e.length - 2; n += 3) {
        var r = e.charAt(n + 2);
        r = "a" <= r ? r.charCodeAt(0) - 87 : Number(r),
        r = "+" === e.charAt(n + 1) ? t >>> r : t << r,
        t = "+" === e.charAt(n) ? t + r & 4294967295 : t ^ r
    }
    return t
}
var r = "320305.131321201"
function ee(t) {
            var o, i = t.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
            if (null === i) {
                var a = t.length;
                a > 30 && (t = "".concat(t.substr(0, 10)).concat(t.substr(Math.floor(a / 2) - 5, 10)).concat(t.substr(-10, 10)))
            } else {
                for (var s = t.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/), c = 0, u = s.length, l = []; c < u; c++)
                    "" !== s[c] && l.push.apply(l, function(t) {
                        if (Array.isArray(t))
                            return e(t)
                    }(o = s[c].split("")) || function(t) {
                        if ("undefined" != typeof Symbol && null != t[Symbol.iterator] || null != t["@@iterator"])
                            return Array.from(t)
                    }(o) || function(t, n) {
                        if (t) {
                            if ("string" == typeof t)
                                return e(t, n);
                            var r = Object.prototype.toString.call(t).slice(8, -1);
                            return "Object" === r && t.constructor && (r = t.constructor.name),
                            "Map" === r || "Set" === r ? Array.from(t) : "Arguments" === r || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? e(t, n) : void 0
                        }
                    }(o) || function() {
                        throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")
                    }()),
                    c !== u - 1 && l.push(i[c]);
                var p = l.length;
                p > 30 && (t = l.slice(0, 10).join("") + l.slice(Math.floor(p / 2) - 5, Math.floor(p / 2) + 5).join("") + l.slice(-10).join(""))
            }
            for (var d = "".concat(String.fromCharCode(103)).concat(String.fromCharCode(116)).concat(String.fromCharCode(107)), h = (null !== r ? r : (r = window[d] || "") || "").split("."), f = Number(h[0]) || 0, m = Number(h[1]) || 0, g = [], y = 0, v = 0; v < t.length; v++) {
                var _ = t.charCodeAt(v);
                _ < 128 ? g[y++] = _ : (_ < 2048 ? g[y++] = _ >> 6 | 192 : (55296 == (64512 & _) && v + 1 < t.length && 56320 == (64512 & t.charCodeAt(v + 1)) ? (_ = 65536 + ((1023 & _) << 10) + (1023 & t.charCodeAt(++v)),
                g[y++] = _ >> 18 | 240,
                g[y++] = _ >> 12 & 63 | 128) : g[y++] = _ >> 12 | 224,
                g[y++] = _ >> 6 & 63 | 128),
                g[y++] = 63 & _ | 128)
            }
            for (var b = f, w = "".concat(String.fromCharCode(43)).concat(String.fromCharCode(45)).concat(String.fromCharCode(97)) + "".concat(String.fromCharCode(94)).concat(String.fromCharCode(43)).concat(String.fromCharCode(54)), k = "".concat(String.fromCharCode(43)).concat(String.fromCharCode(45)).concat(String.fromCharCode(51)) + "".concat(String.fromCharCode(94)).concat(String.fromCharCode(43)).concat(String.fromCharCode(98)) + "".concat(String.fromCharCode(43)).concat(String.fromCharCode(45)).concat(String.fromCharCode(102)), x = 0; x < g.length; x++)
                b = n(b += g[x], w);
            return b = n(b, k),
            (b ^= m) < 0 && (b = 2147483648 + (2147483647 & b)),
            "".concat((b %= 1e6).toString(), ".").concat(b ^ f)
        }
    ''')
        self.url = "https://fanyi.baidu.com/v2transapi"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.37",
            "Cookie": "BAIDUID=5AF46A86F66A064D6EBE8F6CF1D19F1A:FG=1; BAIDUID_BFESS=5AF46A86F66A064D6EBE8F6CF1D19F1A:FG=1; APPGUIDE_10_0_2=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1673791125; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1673791125; ab_sr=1.0.1_ZDI2MmE5YjY3OTk5ZWRmMzMyYzQ4NWNjNjc0OTEyYzU5NWI3YTE4OTE4ZmNiYTU4YTg5MjMwNTI3MTI1OTFjNGE0N2EwMzM3ODZiMTE5NDFhOTQ4YmZjYmUwMDVlZGMzNWNjMDJjZmZjMTBmOWIzNmVlNjMxZmQ3ZDdhNWVjYTNiM2U0MTYxNmNmNmI0NjI0OTgxYWFmMjM1NGUzMGRkZQ==",
            "Acs-Token": "1673769896714_1673791328673_/jNTmMdug05eaCQYNoVx12H//AUDvT1OVFIc1YEyP35x5FqBhdI1kuYKANBm/la3C+OXMEJUUb6VTnUeapUl+WXq9MjdV6J9/DlVJ0judQVWZCq/D7FDCatiFVp6520RnLlIa4nXdEvGkwCuIqItTVzTJnVP5+6c2abzI8OzRlKHemqIHawSr95ZGTxoy3/jV7KFDATPFWQWy22tqXvK3xrshmdx2sIjgQSeB3Ram6ihv1t5BQLCX3izFMzOipG6MFpCeHP3dVYMFadaqHso5VkPxTV+H5UG3SEp6qCwe9XGadzvL4UowwsJjPgsFyDHGiSjYJzuPnxC9RLnKUuThA=="
        }
        self.data = {
            "from": "en",
            "to": "zh",
            "query": "",  # query 即我们要翻译的的内容
            "transtype": "translang",
            "simple_means_flag": "3",
            "sign": "",  # sign 是变化的需要我们执行js代码得到
            "token": "01285396260689477642011522"  # token没有变化
        }

    def translate(self, query):
        """
        通过构造的新的表单数据，访问api，获取翻译内容
        :return:
        """
        response = {"errno": "", "errmsg": ""}
        try:
            self.data['sign'] = self.ctx.call('ee', query)
            self.data['query'] = query
            response = requests.post(self.url, headers=self.headers, data=self.data).json()
            # print(response)
            x = response['trans_result']['data'][0]['dst']
            return x
        except Exception:
            traceback.print_exc()
            print(query + " err " + str(response["errno"]) + "-" + response["errmsg"])
            return query


if __name__ == '__main__':
    baiduTranslate = BaiduTranslateJS()
    result = baiduTranslate.translate("test")
    print(result)
