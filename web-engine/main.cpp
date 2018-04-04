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
    view.setUrl(QUrl(QStringLiteral("http://localhost:8888/pdfjs/web/viewer.html")));
    //view.setUrl(QUrl(QStringLiteral("https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/pdf_open_parameters.pdf")));
    //view.setUrl(QUrl(QStringLiteral("https://mozilla.github.io/pdf.js/web/viewer.html")));
    view.resize(1200, 1000);
    view.show();

    return app.exec();
}
