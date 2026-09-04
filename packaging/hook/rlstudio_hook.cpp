#define _GNU_SOURCE
#include <dlfcn.h>
#include <QString>
#include <QWidget>
#include <QGuiApplication>
#include <QUrl>
#include <QDesktopServices>

namespace
{
    QString cleanTitle(QString t)
    {
        if (t.isEmpty())
            return t;
        t.replace("Krita", "RLStudio");
        t.replace("KRITA", "RLSTUDIO");
        t.replace("krita", "rlstudio");
        return t;
    }
} // namespace

// 1. Hook QWidget::setWindowTitle to change all window & dialog titles
typedef void (*SetWindowTitleFn)(QWidget *, const QString &);
static SetWindowTitleFn orig_setWindowTitle = nullptr;

extern "C" void _ZN7QWidget14setWindowTitleERK7QString(QWidget *self, const QString &title)
{
    if (!orig_setWindowTitle)
    {
        orig_setWindowTitle = (SetWindowTitleFn)dlsym(RTLD_NEXT, "_ZN7QWidget14setWindowTitleERK7QString");
    }
    QString sanitized = cleanTitle(title);
    if (orig_setWindowTitle)
    {
        orig_setWindowTitle(self, sanitized);
    }
}

// 2. Hook QGuiApplication::setApplicationDisplayName
typedef void (*SetAppDisplayNameFn)(const QString &);
static SetAppDisplayNameFn orig_setAppDisplayName = nullptr;

extern "C" void _ZN15QGuiApplication25setApplicationDisplayNameERK7QString(const QString &name)
{
    if (!orig_setAppDisplayName)
    {
        orig_setAppDisplayName = (SetAppDisplayNameFn)dlsym(RTLD_NEXT, "_ZN15QGuiApplication25setApplicationDisplayNameERK7QString");
    }
    QString appName = QStringLiteral("RLStudio");
    if (orig_setAppDisplayName)
    {
        orig_setAppDisplayName(appName);
    }
}

// 3. Hook QDesktopServices::openUrl to redirect RLStudio Web and Krita links to GitHub
typedef bool (*OpenUrlFn)(const QUrl &);
static OpenUrlFn orig_openUrl = nullptr;

extern "C" bool _ZN16QDesktopServices7openUrlERK4QUrl(const QUrl &url)
{
    if (!orig_openUrl)
    {
        orig_openUrl = (OpenUrlFn)dlsym(RTLD_NEXT, "_ZN16QDesktopServices7openUrlERK4QUrl");
    }
    QString urlStr = url.toString();
    // Redirect RLStudio Web and Krita website / donation links to GitHub repo
    if (urlStr.contains("krita.org") || urlStr.contains("RLStudio") || urlStr.contains("donations"))
    {
        QUrl githubUrl(QStringLiteral("https://github.com/RetakJunior/RL-Studio"));
        return orig_openUrl ? orig_openUrl(githubUrl) : false;
    }
    return orig_openUrl ? orig_openUrl(url) : false;
}

// 4. Hook KAboutData::displayName
extern "C" QString _ZNK10KAboutData11displayNameEv(const void * /*self*/)
{
    return QStringLiteral("RLStudio");
}

// 5. Hook KAboutData::productName
extern "C" QString _ZNK10KAboutData11productNameEv(const void * /*self*/)
{
    return QStringLiteral("RLStudio");
}
