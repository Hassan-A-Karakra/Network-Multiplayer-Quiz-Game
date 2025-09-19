import java.net.ServerSocket;
import java.net.Socket;
import java.io.*;

public class Server {
    public static void main(String[] args) {
        // Calculate port from student ID: last 3 digits + 5000
        int studentId = 1221058; 
        int lastThreeDigits = studentId % 1000; 
        int port = lastThreeDigits + 5000; // 058 + 5000 = 5058
        
        try (ServerSocket server = new ServerSocket(port)) {
            System.out.println("Server is listening on port: " + port);
            System.out.println("-------------------------------------------------");

            while (true) {
                try (Socket socket = server.accept()) {
                    handleClient(socket, port);
                } catch (Exception e) {
                    e.printStackTrace();
                    System.out.println("Client ERROR");
                }
            }

        } catch (IOException e) {
            System.out.println("Server ERROR: check if port is available and use correct IPv4 address");
        }
    }

    private static void handleClient(Socket socket, int port) throws IOException {
        try (BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             OutputStream outputStream = socket.getOutputStream()) {

            String line = in.readLine();
            if (line == null) return;

            System.out.println("Request: " + line);
            System.out.println("-------------------------------------------------");

            String[] requestParts = line.split(" ");
            if (requestParts.length < 2) {
                send400(out, socket, port);
                return;
            }

            String requestedPath = requestParts[1];
            
           
            if (requestedPath.contains("file=")) {
                handleFileRequest(out, outputStream, socket, port, requestedPath);
                return;
            }

      
            if (requestedPath.equals("/") || requestedPath.equals("/index.html") || 
                requestedPath.equals("/main_en.html") || requestedPath.equals("/en")) {
                requestedPath = "/html/main_en.html";
            } else if (requestedPath.equals("/ar") || requestedPath.equals("/main_ar.html")) {
                requestedPath = "/html/main_ar.html";
            } else if (requestedPath.equals("/T010_1221058_en.html")) {
                requestedPath = "/html/T010_1221058_en.html";
            } else if (requestedPath.equals("/T010_1221058_ar.html")) {
                requestedPath = "/html/T010_1221058_ar.html";
            }

     
            if (requestedPath.toLowerCase().contains("private")) {
                send403(out, socket, port, "Access Denied – This file is private.");
                return;
            }

            File file = new File("." + requestedPath);

            if (file.exists() && !file.isDirectory()) {
                send200(file, requestedPath, socket, out, outputStream, port);
            } else {
                send404(out, socket, port, "The file is not found.");
            }
        }
    }

    private static void handleFileRequest(PrintWriter out, OutputStream outputStream, 
                                        Socket socket, int port, String requestPath) throws IOException {
       
        String filename = null;
        String[] queryParts = requestPath.split("\\?");
        if (queryParts.length > 1) {
            String[] params = queryParts[1].split("&");
            for (String param : params) {
                if (param.startsWith("file=")) {
                    filename = param.substring(5); 
                    
                    filename = java.net.URLDecoder.decode(filename, "UTF-8");
                    break;
                }
            }
        }

        if (filename == null || filename.isEmpty()) {
            send400(out, socket, port);
            return;
        }

       
        if (filename.toLowerCase().contains("private")) {
            send403(out, socket, port, "Access Denied – This file is private.");
            return;
        }

        File file = new File("." + File.separator + filename);
        if (file.exists() && !file.isDirectory()) {
            send200(file, filename, socket, out, outputStream, port);
        } else {
            send404(out, socket, port, "The file is not found.");
        }
    }

    private static void send200(File file, String requestedFile, Socket socket, 
                               PrintWriter out, OutputStream outputStream, int port) throws IOException {
        String contentType = getContentType(requestedFile);

        out.println("HTTP/1.1 200 OK");
        out.println("Content-Type: " + contentType);
        out.println("Content-Length: " + file.length());
        out.println();

        
        if (contentType.startsWith("image/") || contentType.equals("video/mp4") || 
            contentType.equals("application/pdf")) {
            try (FileInputStream fis = new FileInputStream(file)) {
                byte[] buffer = new byte[4096];
                int bytesRead;
                while ((bytesRead = fis.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, bytesRead);
                }
                outputStream.flush();
            }
        } else { 
            try (BufferedReader fileReader = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = fileReader.readLine()) != null) {
                    out.println(line);
                }
                out.flush();
            }
        }

        System.out.println(requestedFile + " served successfully.");
        System.out.println("Response Code: 200 OK");
        System.out.println("Client IP: " + socket.getInetAddress().getHostAddress());
        System.out.println("Client Port: " + socket.getPort());
        System.out.println("Server Port: " + port);
        System.out.println("-------------------------------------------------");
    }

    private static void send404(PrintWriter out, Socket socket, int port, String message) {
        String errMsg = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Error 404</title></head>"
                + "<body><h1>Error 404</h1><h2 style='color:red;'>" + message + "</h2>"
                + "<p>Client IP: " + socket.getInetAddress().getHostAddress() + "</p>"
                + "<p>Client Port: " + socket.getPort() + "</p></body></html>";

        out.println("HTTP/1.1 404 Not Found");
        out.println("Content-Type: text/html; charset=UTF-8");
        out.println("Content-Length: " + errMsg.getBytes().length);
        out.println();
        out.print(errMsg);
        out.flush();

        System.out.println("Response Code: 404 Not Found");
        System.out.println("Client IP: " + socket.getInetAddress().getHostAddress());
        System.out.println("Client Port: " + socket.getPort());
        System.out.println("Server Port: " + port);
        System.out.println("-------------------------------------------------");
    }

    private static void send403(PrintWriter out, Socket socket, int port, String message) {
        String msg = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Error 403</title></head>"
                + "<body><h1>Error 403 Forbidden</h1>"
                + "<p>" + message + "</p>"
                + "<p>Client IP: " + socket.getInetAddress().getHostAddress() + "</p>"
                + "<p>Client Port: " + socket.getPort() + "</p></body></html>";

        out.println("HTTP/1.1 403 Forbidden");
        out.println("Content-Type: text/html; charset=UTF-8");
        out.println("Content-Length: " + msg.getBytes().length);
        out.println();
        out.print(msg);
        out.flush();

        System.out.println("Response Code: 403 Forbidden");
        System.out.println("Client IP: " + socket.getInetAddress().getHostAddress());
        System.out.println("Client Port: " + socket.getPort());
        System.out.println("Server Port: " + port);
        System.out.println("-------------------------------------------------");
    }

    private static void send400(PrintWriter out, Socket socket, int port) {
        String msg = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Error 400</title></head>"
                + "<body><h1>Error 400 Bad Request</h1>"
                + "<p>Invalid request.</p>"
                + "<p>Client IP: " + socket.getInetAddress().getHostAddress() + "</p>"
                + "<p>Client Port: " + socket.getPort() + "</p></body></html>";

        out.println("HTTP/1.1 400 Bad Request");
        out.println("Content-Type: text/html; charset=UTF-8");
        out.println("Content-Length: " + msg.getBytes().length);
        out.println();
        out.print(msg);
        out.flush();

        System.out.println("Response Code: 400 Bad Request");
        System.out.println("Client IP: " + socket.getInetAddress().getHostAddress());
        System.out.println("Client Port: " + socket.getPort());
        System.out.println("Server Port: " + port);
        System.out.println("-------------------------------------------------");
    }

    private static String getContentType(String filePath) {
        if (filePath.endsWith(".html")) return "text/html";
        if (filePath.endsWith(".css")) return "text/css";
        if (filePath.endsWith(".png")) return "image/png";
        if (filePath.endsWith(".jpg") || filePath.endsWith(".jpeg")) return "image/jpeg";
        if (filePath.endsWith(".mp4")) return "video/mp4";
        if (filePath.endsWith(".pdf")) return "application/pdf";
        return "text/plain";
    }
}