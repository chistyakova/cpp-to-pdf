#ifndef WEBSERVER_H
#define WEBSERVER_H

#include <QObject>
#include <QThread>

#include "mongoose.h"

static struct mg_serve_http_opts s_http_server_opts;

class WebServer : public QThread
{
    Q_OBJECT
public:
    WebServer();
    void run();
    static void ev_handler(struct mg_connection *, int, void *);
};

#endif // WEBSERVER_H
