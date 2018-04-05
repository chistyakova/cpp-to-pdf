#include <QApplication>
#include <QWebEngineView>
#include <QWebEnginePage>

#include "webserver.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    WebServer s;
    s.start();

    QWebEngineView view;
    view.setUrl(QUrl(QStringLiteral("http://localhost:8888/pdfjs/web/viewer.html?file=")));
    view.resize(900, 500);
    view.show();

    return app.exec();
}
