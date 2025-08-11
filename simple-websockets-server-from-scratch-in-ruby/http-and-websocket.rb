require 'socket'
require 'digest/sha1'

server = TCPServer.new('localhost', 2345)

loop do
  socket = server.accept
  STDERR.puts "Incoming Request"

  http_request = ""
  while (line = socket.gets) && (line != "\r\n")
    http_request += line
  end

  if matches = http_request.match(/^Sec-WebSocket-Key: (\S+)/)
    # --- WebSocket handshake ---
    websocket_key = matches[1]
    response_key = Digest::SHA1.base64digest([websocket_key, "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"].join)

    socket.write <<~EOS
      HTTP/1.1 101 Switching Protocols
      Upgrade: websocket
      Connection: Upgrade
      Sec-WebSocket-Accept: #{response_key}

    EOS
    STDERR.puts "WebSocket connected"

    # （WebSocketフレーム処理をここに書く）
  else
    # --- 普通のHTTPレスポンス ---
    html = <<~HTML
      <!DOCTYPE html>
      <html>
      <body>
        <h1>Hello from Ruby WebSocket Server</h1>
        <script>
          let ws = new WebSocket("ws://localhost:2345");
          ws.onopen = () => console.log("WebSocket connected!");
        </script>
      </body>
      </html>
    HTML

    socket.write "HTTP/1.1 200 OK\r\n"
    socket.write "Content-Type: text/html\r\n"
    socket.write "Content-Length: #{html.bytesize}\r\n"
    socket.write "\r\n"
    socket.write html
    socket.close
  end
end

