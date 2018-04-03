#include <QApplication>
#include <QWebEngineView>

#include "webserver.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    WebServer s;
    s.start();

    QWebEngineView view;
    view.setUrl(QUrl(QStringLiteral("http://localhost:8888")));
    view.resize(1024, 750);
    view.show();

    return app.exec();
}
