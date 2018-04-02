#include <QApplication>
#include <QWebEngineView>

#include "webserver.h"

QUrl commandLineUrlArgument()
{
    const QStringList args = QCoreApplication::arguments();
    for (const QString &arg : args.mid(1)) {
        if (!arg.startsWith(QLatin1Char('-')))
            return QUrl::fromUserInput(arg);
    }
    return QUrl(QStringLiteral("http://localhost:8888"));
}

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);

    WebServer s;
    s.start();

    QWebEngineView view;
    view.setUrl(commandLineUrlArgument());
    view.resize(1024, 750);
    view.show();

    return app.exec();
}
