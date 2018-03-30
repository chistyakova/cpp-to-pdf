#include <QApplication>
#include <QWebEngineView>

#include "mongoose.h"

QUrl commandLineUrlArgument()
{
    const QStringList args = QCoreApplication::arguments();
    for (const QString &arg : args.mid(1)) {
        if (!arg.startsWith(QLatin1Char('-')))
            return QUrl::fromUserInput(arg);
    }
    return QUrl(QStringLiteral("http://pm.core.raa-st.ru"));
}

static const char *s_http_port = "8888";
static struct mg_serve_http_opts s_http_server_opts;

static void ev_handler(struct mg_connection *nc, int ev, void *ev_data) {
  struct http_message *hm = (struct http_message *) ev_data;

  switch (ev) {
    case MG_EV_HTTP_REQUEST:
      if      (mg_vcmp(&hm->uri, "/api/stop")  == 0) {  }
      else if (mg_vcmp(&hm->uri, "/api/status") == 0) {  }
      else {
        mg_serve_http(nc, hm, s_http_server_opts); /* Serve static content */
      }
      break;
    default:
      break;
  }
}

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);



    struct mg_mgr mgr;
      struct mg_connection *nc;
      char *cp;
      std::string document_root = ".";

      // аЄаАаЙаЛ index.html аДаОаЛаЖаЕаН аБббб баАбаПаОаЛаОаЖаЕаН аНаА аОаДаНб аДаИбаЕаКбаОбаИб аВаВаЕбб
      // аОб аИбаПаОаЛаНбаЕаМаОаГаО баАаЙаЛаА аВ аДаИбаЕаКбаОбаИаИ www
      if (argc > 0 && ((cp = strrchr(argv[0], DIRSEP)) != NULL)) {
        *cp = '\0';
        document_root = std::string(argv[0]);
      }

      chdir(document_root.c_str());

      s_http_server_opts.document_root = document_root.c_str();

      mg_mgr_init(&mgr, NULL);
      nc = mg_bind(&mgr, s_http_port, ev_handler);
      if (nc == NULL) {
        printf("Error mg_bind\n");
        exit(1);
      }

      mg_set_protocol_http_websocket(nc);
      s_http_server_opts.enable_directory_listing = "yes";

      printf("port = %s\n", s_http_port);
      printf("s_http_server_opts.document_root = %s\n",s_http_server_opts.document_root);
      for (;;) {
        mg_mgr_poll(&mgr, 1000);
      }
      mg_mgr_free(&mgr);



    QWebEngineView view;
    view.setUrl(commandLineUrlArgument());
    view.resize(1024, 750);
    view.show();

    return app.exec();
}
