#include "webserver.h"
#include <QFileInfo>
#include <QCoreApplication>

WebServer::WebServer()
{

}

void WebServer::ev_handler(struct mg_connection *nc, int ev, void *ev_data) {
    struct http_message *hm = (struct http_message *) ev_data;

    switch (ev) {
      case MG_EV_HTTP_REQUEST:
        if      (mg_vcmp(&hm->uri, "/api/request1")  == 0) { }
        else if (mg_vcmp(&hm->uri, "/api/request2") == 0) {  }
        else {
          mg_serve_http(nc, hm, s_http_server_opts);
        }
        break;
      default:
        break;
      }
}

void WebServer::run() {
    struct mg_mgr mgr;
    struct mg_connection *nc;
    QString document_root = QFileInfo(QCoreApplication::applicationFilePath()).absolutePath() + "/../html";
    chdir(document_root.toStdString().c_str());
    s_http_server_opts.document_root = ".";

    mg_mgr_init(&mgr, NULL);
    nc = mg_bind(&mgr, "8888", WebServer::ev_handler);
    if (nc == NULL) {
      printf("Error mg_bind\n");
      exit(1);
    }

    mg_set_protocol_http_websocket(nc);
    s_http_server_opts.enable_directory_listing = "yes";

    while(true) {
      mg_mgr_poll(&mgr, 1000);
    }
    mg_mgr_free(&mgr);
}





