// 관리자(/admin) GitHub 로그인 시작
const crypto = require('crypto');
module.exports = (req, res) => {
  const id = process.env.GITHUB_CLIENT_ID;
  if (!id) { res.status(500).send('GITHUB_CLIENT_ID 환경변수가 설정되지 않았습니다.'); return; }
  const state = crypto.randomBytes(16).toString('hex');
  res.setHeader('Set-Cookie', `oauth_state=${state}; HttpOnly; Secure; Path=/; Max-Age=600; SameSite=Lax`);
  const url = 'https://github.com/login/oauth/authorize?client_id=' + encodeURIComponent(id) +
    '&scope=repo&state=' + state;
  res.redirect(302, url);
};
