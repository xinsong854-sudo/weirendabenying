# 伪人大本营反向代理配置

目标：用自己的域名代理当前 Cohub 3000 服务，让用户访问更干净的地址。

当前源站：

```text
https://s-63a86395-de5c-46f9-a54d-0f7d02aa0671-3000.cohub.run
```

## 推荐方案

### 方案 A：Cloudflare Worker / Pages Function

适合：已经有域名托管在 Cloudflare，想最快获得 `https://你的域名/...`。

使用文件：

```text
cloudflare-worker.js
```

部署后将 Worker 绑定到你的域名或子域名，例如：

```text
https://nieta.example.com
```

可选环境变量：

```text
COHUB_ORIGIN=https://s-63a86395-de5c-46f9-a54d-0f7d02aa0671-3000.cohub.run
```

如果没有配置环境变量，脚本会默认使用上面的 Cohub 源站。

### 方案 B：Caddy

适合：有自己的 VPS，想自动签 HTTPS 证书。

使用文件：

```text
Caddyfile
```

把 `your-domain.example.com` 替换成你的域名，然后运行：

```bash
caddy run --config Caddyfile
```

### 方案 C：Nginx

适合：已有 Nginx 服务器。

使用文件：

```text
nginx.conf
```

把 `your-domain.example.com` 替换成你的域名，并按你的证书路径调整 SSL 配置。

## 验证清单

部署后访问你的域名，检查：

- 首页能打开
- 静态资源能加载
- `/api/forum/posts` 这类接口返回正常
- 手机号验证码登录流程正常
- 发帖、身份卡、Wiki 投稿等动态功能正常

## 注意

- 反代本身不会保存手机号、验证码或 Token。
- 源站 Cohub 3000 服务仍需保持运行。
- 若后续有正式后端，应把源站地址从 Cohub 预览域名换成正式服务地址。
