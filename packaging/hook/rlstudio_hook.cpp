#define _GNU_SOURCE
#include <dlfcn.h>
#include <QString>
#include <QWidget>
#include <QGuiApplication>
#include <QUrl>
#include <QDesktopServices>
#include <QIcon>
#include <QPixmap>
#include <QFile>

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

    QIcon getRLIcon()
    {
        static QIcon cachedIcon;
        if (!cachedIcon.isNull())
            return cachedIcon;

        const char *appdir = getenv("APPDIR");
        QStringList candidates;
        if (appdir)
        {
            candidates << QString(appdir) + "/usr/share/icons/hicolor/256x256/apps/rlstudio.png";
            candidates << QString(appdir) + "/rlstudio.png";
        }
        candidates << QStringLiteral("/home/retak/Şablonlar/RetakAlium Studio/logos/logo.png");
        candidates << QStringLiteral("/tmp/rlstudio_icon.png");

        for (const QString &path : candidates)
        {
            if (QFile::exists(path))
            {
                cachedIcon = QIcon(path);
                break;
            }
        }
        return cachedIcon;
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

// 2. Hook QWidget::setWindowIcon to ensure canvas/subwindow/dialogs use RL Studio icon
typedef void (*SetWindowIconFn)(QWidget *, const QIcon &);
static SetWindowIconFn orig_setWindowIcon = nullptr;

extern "C" void _ZN7QWidget13setWindowIconERK5QIcon(QWidget *self, const QIcon &icon)
{
    if (!orig_setWindowIcon)
    {
        orig_setWindowIcon = (SetWindowIconFn)dlsym(RTLD_NEXT, "_ZN7QWidget13setWindowIconERK5QIcon");
    }
    QIcon rl = getRLIcon();
    if (!rl.isNull())
    {
        if (orig_setWindowIcon)
            orig_setWindowIcon(self, rl);
        return;
    }
    if (orig_setWindowIcon)
        orig_setWindowIcon(self, icon);
}

// 3. Hook QGuiApplication::setApplicationDisplayName
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

// 4. Hook QDesktopServices::openUrl to redirect RLStudio Web and Krita links to GitHub
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

// 5. Hook KAboutData::displayName
extern "C" QString _ZNK10KAboutData11displayNameEv(const void * /*self*/)
{
    return QStringLiteral("RLStudio");
}

// 6. Hook KAboutData::productName
extern "C" QString _ZNK10KAboutData11productNameEv(const void * /*self*/)
{
    return QStringLiteral("RLStudio");
}
