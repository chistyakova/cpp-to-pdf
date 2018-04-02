TEMPLATE = app

QT += core widgets webenginewidgets

SOURCES += main.cpp mongoose.c \
    webserver.cpp
HEADERS += mongoose.h \
    webserver.h

win32:LIBS += -ladvapi32 -luser32

target.path = $$[QT_INSTALL_EXAMPLES]/webenginewidgets/minimal
INSTALLS += target
