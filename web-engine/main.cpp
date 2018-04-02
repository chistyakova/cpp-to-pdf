#include <QApplication>
#include <QWebEngineView>
#include <QThread>
#include "mongoose.h"

QUrl commandLineUrlArgument()
{
    const QStringList args = QCoreApplication::arguments();
    for (const QString &arg : args.mid(1)) {
        if (!arg.startsWith(QLatin1Char('-')))
            return QUrl::fromUserInput(arg);
    }
    return QUrl(QStringLiteral("http://localhost:8888"));
}

class WorkerThread : public QThread
{
    Q_OBJECT
public:
    static struct mg_serve_http_opts s_http_server_opts;

    static void ev_handler(struct mg_connection *nc, int ev, void *ev_data) {
        struct http_message *hm = (struct http_message *) ev_data;

        switch (ev) {
          case MG_EV_HTTP_REQUEST:
            if      (mg_vcmp(&hm->uri, "/api/stop")  == 0) {  }
            else if (mg_vcmp(&hm->uri, "/api/status") == 0) {  }
            else {
              mg_serve_http(nc, hm, s_http_server_opts);
            }
            break;
          default:
            break;
          }
    }

    void run() override {
        /* ... here is the expensive or blocking operation ... */
        struct mg_mgr mgr;
        struct mg_connection *nc;
        std::string document_root = ".";

        chdir(document_root.c_str());

        //WorkerThread::s_http_server_opts.document_root = document_root.c_str();

        mg_mgr_init(&mgr, NULL);
        nc = mg_bind(&mgr, "8888", WorkerThread::ev_handler);
        if (nc == NULL) {
          printf("Error mg_bind\n");
          exit(1);
        }

        mg_set_protocol_http_websocket(nc);
        //WorkerThread::s_http_server_opts.enable_directory_listing = "yes";

        for (;;) {
          mg_mgr_poll(&mgr, 1000);
        }
        mg_mgr_free(&mgr);
    }
};

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);

    WorkerThread *workerThread = new WorkerThread();
    workerThread->start();

    QWebEngineView view;
    view.setUrl(commandLineUrlArgument());
    view.resize(1024, 750);
    view.show();

    return app.exec();
}