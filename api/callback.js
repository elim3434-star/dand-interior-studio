// GitHub 로그인 완료 후 관리자 화면에 토큰 전달
module.exports = async (req, res) => {
  const { code, state } = req.query || {};
  const cookie = (req.headers.cookie || '').split(';').map(s => s.trim()).find(s => s.startsWith('oauth_state='));
  const saved = cookie ? cookie.split('=')[1] : '';
  const allowed = process.env.SITE_ORIGIN || '';   // 예: https://example.com (설정 권장)
  const done = (status, payload) => {
    const msg = 'authorization:github:' + status + ':' + JSON.stringify(payload);
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(200).send(`<!doctype html><meta charset="utf-8"><body><p>${status === 'success' ? '로그인되었습니다. 창이 곧 닫힙니다.' : '로그인에 실패했습니다.'}</p><script>
(function(){
  var allowed=${JSON.stringify(allowed)};
  function receive(e){
    if(allowed && e.origin!==allowed) return;
    window.opener.postMessage(${JSON.stringify(msg)}, e.origin);
    window.removeEventListener('message', receive, false);
    setTimeout(function(){window.close()},300);
  }
  window.addEventListener('message', receive, false);
  window.opener && window.opener.postMessage('authorizing:github','*');
})();
</script></body>`);
  };
  try {
    if (!code || !state || state !== saved) return done('error', { message: 'invalid state' });
    const r = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ client_id: process.env.GITHUB_CLIENT_ID, client_secret: process.env.GITHUB_CLIENT_SECRET, code })
    });
    const j = await r.json();
    if (!j.access_token) return done('error', j);
    return done('success', { token: j.access_token, provider: 'github' });
  } catch (err) {
    return done('error', { message: String(err) });
  }
};
