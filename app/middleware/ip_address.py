from starlette.types import ASGIApp, Receive, Scope, Send

class RealIPMiddleware:
    """
    Middleware для определения реального IP-адреса пользователя.
    Поддерживает работу за Nginx, Cloudflare и другими прокси.
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Словарь для удобного поиска по заголовкам
        headers = dict(scope.get("headers", []))
        
        # 1. Проверяем заголовок Cloudflare (если используете его)
        # Заголовки в ASGI хранятся в байтах и в нижнем регистре!
        real_ip = headers.get(b"cf-connecting-ip")

        # 2. Проверяем стандартный X-Forwarded-For (Nginx, ALB, Traefik)
        if not real_ip:
            x_forwarded_for = headers.get(b"x-forwarded-for")
            if x_forwarded_for:
                # X-Forwarded-For может содержать цепочку IP через запятую.
                # Первый IP в списке — это всегда изначальный клиент.
                real_ip = x_forwarded_for.decode("utf-8").split(",")[0].strip().encode()

        # 3. Проверяем X-Real-IP
        if not real_ip:
            real_ip = headers.get(b"x-real-ip")

        # 4. Если прокси нет, берем IP напрямую из клиентского соединения
        if real_ip:
            client_ip = real_ip.decode("utf-8")
        else:
            client_ip = scope.get("client", ["unknown"])[0]

        # Записываем определенный IP в scope, чтобы он был доступен в FastAPI
        scope["state"] = scope.get("state", {})
        scope["state"]["user_ip"] = client_ip
        
        await self.app(scope, receive, send)