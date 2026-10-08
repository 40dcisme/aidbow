"""CDP 冒烟：无头浏览器加载评审页 → 勾选/优先级/备注 → 校验导出内容。

零新增依赖（websockets 已在本机环境）。用法：
    python smoke_cdp.py <url>
"""
import asyncio
import json
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets


class CDP:
    def __init__(self, ws_url):
        self.ws = None
        self.ws_url = ws_url
        self._id = 0

    async def __aenter__(self):
        self.ws = await websockets.connect(self.ws_url, max_size=64 * 1024 * 1024)
        return self

    async def __aenter2__(self):
        return self

    async def __aexit__(self, *a):
        await self.ws.close()

    async def call(self, method, **params):
        self._id += 1
        mid = self._id
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method} -> {msg['error']}")
                return msg.get("result", {})

    async def eval(self, expr, await_promise=False):
        r = await self.call("Runtime.evaluate", expression=expr,
                           returnByValue=True, awaitPromise=await_promise)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"], ensure_ascii=False)[:600])
        return r.get("result", {}).get("value")


async def main(url):
    port = 9333
    prof = tempfile.mkdtemp(prefix="edge-cdp-")
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    proc = subprocess.Popen([
        edge, "--headless=new", "--disable-gpu", f"--remote-debugging-port={port}",
        f"--user-data-dir={prof}", "about:blank"])
    try:
        ws_url = None
        for _ in range(40):
            try:
                tabs = json.load(urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/json"))
                pages = [t for t in tabs if t.get("type") == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.25)
        assert ws_url, "Edge CDP 未就绪"

        async with CDP(ws_url) as cdp:
            await cdp.call("Page.enable")
            await cdp.call("Page.navigate", url=url)
            await asyncio.sleep(1.5)

            # 1) 初始渲染
            n = await cdp.eval("document.querySelectorAll('#list .card').length")
            total = await cdp.eval("document.getElementById('nTotal').textContent")
            assert n == 4 and total == "4", f"初始卡片数异常 {n}/{total}"

            # 2) 勾选第一张 + 选 P0 + 写备注（直接派发事件模拟用户操作）
            js = """
            (function(){
              var id='alpha:01';
              var cb=document.querySelector('.cb[data-id="'+id+'"]');
              cb.checked=true; cb.dispatchEvent(new Event('click',{bubbles:true}));
              var sel=document.querySelector('.prio[data-id="'+id+'"]');
              sel.value='P0'; sel.dispatchEvent(new Event('change',{bubbles:true}));
              var nt=document.querySelector('.note[data-id="'+id+'"]');
              nt.value='冒烟备注：通过'; nt.dispatchEvent(new Event('input',{bubbles:true}));
              return document.getElementById('nPicked').textContent;
            })()
            """
            picked = await cdp.eval(js)
            assert picked == "1", f"勾选计数 {picked}"

            # 3) 搁置 alpha:02
            await cdp.eval("""
              (function(){var s=document.querySelector('.prio[data-id="alpha:02"]');
                s.value='shelved'; s.dispatchEvent(new Event('change',{bubbles:true})); return 1;})()
            """)

            # 4) localStorage 持久化
            ls = await cdp.eval(
                "JSON.parse(localStorage.getItem('aidbow-review-ui:demo-park-weekend'))['alpha:01'].priority")
            assert ls == "P0", f"localStorage {ls}"

            # 5) 导出内容校验（点击按钮后从弹窗读文本）
            await cdp.eval("document.getElementById('doMd').click()")
            md_text = await cdp.eval("document.getElementById('outText').value")
            assert "评审决策单 · demo-park-weekend" in md_text
            assert "P0 · 立即做" in md_text
            assert "冒烟备注：通过" in md_text
            assert "搁置（1）" in md_text

            j_text = await cdp.eval("""
              (function(){document.getElementById('doJson').click();
                return document.getElementById('outText').value;})()
            """)
            dec = json.loads(j_text)
            assert dec["selected"] == ["alpha:01"], dec
            assert dec["priorities"]["alpha:01"] == "P0"
            assert dec["priorities"]["alpha:02"] == "shelved"
            assert dec["notes"]["alpha:01"] == "冒烟备注：通过"

            # 6) 筛选
            await cdp.eval("""
              (function(){var f=document.getElementById('fRound');f.value='R2';
                f.dispatchEvent(new Event('change'));return 1;})()
            """)
            n2 = await cdp.eval("document.querySelectorAll('#list .card').length")
            assert n2 == 1, f"R2 筛选后 {n2}"
            await cdp.eval("""
              (function(){var f=document.getElementById('fRound');f.value='';
                f.dispatchEvent(new Event('change'));return 1;})()
            """)

            print("CDP SMOKE OK: 渲染4卡/勾选/P0/备注/搁置/localStorage/MD/JSON/R2筛选 全部通过")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
