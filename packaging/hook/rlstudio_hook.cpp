#define _GNU_SOURCE
#include <dlfcn.h>
#include <QString>
#include <QStringList>
#include <QWidget>
#include <QGuiApplication>
#include <QUrl>
#include <QDesktopServices>
#include <QFileDialog>
#include <QIcon>
#include <QPixmap>
#include <QFile>
#include <QMimeDatabase>
#include <QMimeType>
#include <QMessageBox>

namespace {

QString cleanTitle(QString t) {
    if (t.isEmpty()) return t;
    t.replace("Krita — ", "");
    t.replace("Krita - ", "");
    t.replace(" — Krita", "");
    t.replace(" - Krita", "");
    t.replace("Krita", "RLStudio");
    t.replace("KRITA", "RLSTUDIO");
    t.replace("krita", "rlstudio");
    return t;
}

QString cleanMessage(QString t) {
    if (t.isEmpty()) return t;
    t.replace("Krita", "RLStudio");
    t.replace("KRITA", "RLSTUDIO");
    t.replace("krita", "rlstudio");
    return t;
}

QIcon getRLIcon() {
    static QIcon cachedIcon;
    if (!cachedIcon.isNull()) return cachedIcon;

    const char* appdir = getenv("APPDIR");
    QStringList candidates;
    if (appdir) {
        candidates << QString(appdir) + "/usr/share/icons/hicolor/256x256/apps/rlstudio.png";
        candidates << QString(appdir) + "/rlstudio.png";
    }
    candidates << QStringLiteral("/home/retak/Şablonlar/RetakAlium Studio/logos/logo.png");
    candidates << QStringLiteral("/tmp/rlstudio_icon.png");

    for (const QString& path : candidates) {
        if (QFile::exists(path)) {
            cachedIcon = QIcon(path);
            break;
        }
    }
    return cachedIcon;
}

} // namespace

// 1. Hook QWidget::setWindowTitle
typedef void (*SetWindowTitleFn)(QWidget*, const QString&);
static SetWindowTitleFn orig_setWindowTitle = nullptr;

extern "C" void _ZN7QWidget14setWindowTitleERK7QString(QWidget* self, const QString& title) {
    if (!orig_setWindowTitle) {
        orig_setWindowTitle = (SetWindowTitleFn)dlsym(RTLD_NEXT, "_ZN7QWidget14setWindowTitleERK7QString");
    }
    QString sanitized = cleanTitle(title);
    if (orig_setWindowTitle) {
        orig_setWindowTitle(self, sanitized);
    }
}

// 2. Hook QWidget::setWindowIcon
typedef void (*SetWindowIconFn)(QWidget*, const QIcon&);
static SetWindowIconFn orig_setWindowIcon = nullptr;

extern "C" void _ZN7QWidget13setWindowIconERK5QIcon(QWidget* self, const QIcon& icon) {
    if (!orig_setWindowIcon) {
        orig_setWindowIcon = (SetWindowIconFn)dlsym(RTLD_NEXT, "_ZN7QWidget13setWindowIconERK5QIcon");
    }
    QIcon rl = getRLIcon();
    if (!rl.isNull()) {
        if (orig_setWindowIcon) orig_setWindowIcon(self, rl);
        return;
    }
    if (orig_setWindowIcon) orig_setWindowIcon(self, icon);
}

// 3. Hook QGuiApplication::setApplicationDisplayName
typedef void (*SetAppDisplayNameFn)(const QString&);
static SetAppDisplayNameFn orig_setAppDisplayName = nullptr;

extern "C" void _ZN15QGuiApplication25setApplicationDisplayNameERK7QString(const QString& name) {
    if (!orig_setAppDisplayName) {
        orig_setAppDisplayName = (SetAppDisplayNameFn)dlsym(RTLD_NEXT, "_ZN15QGuiApplication25setApplicationDisplayNameERK7QString");
    }
    QString appName = QStringLiteral("RLStudio");
    if (orig_setAppDisplayName) {
        orig_setAppDisplayName(appName);
    }
}

// 4. Hook QDesktopServices::openUrl
typedef bool (*OpenUrlFn)(const QUrl&);
static OpenUrlFn orig_openUrl = nullptr;

extern "C" bool _ZN16QDesktopServices7openUrlERK4QUrl(const QUrl& url) {
    if (!orig_openUrl) {
        orig_openUrl = (OpenUrlFn)dlsym(RTLD_NEXT, "_ZN16QDesktopServices7openUrlERK4QUrl");
    }
    QString urlStr = url.toString();
    if (urlStr.contains("krita.org") || urlStr.contains("RLStudio") || urlStr.contains("donations")) {
        QUrl githubUrl(QStringLiteral("https://github.com/RetakJunior/RL-Studio"));
        return orig_openUrl ? orig_openUrl(githubUrl) : false;
    }
    return orig_openUrl ? orig_openUrl(url) : false;
}

// 5. Hook KAboutData
extern "C" QString _ZNK10KAboutData11displayNameEv(const void* /*self*/) {
    return QStringLiteral("RLStudio");
}

extern "C" QString _ZNK10KAboutData11productNameEv(const void* /*self*/) {
    return QStringLiteral("RLStudio");
}

// 6. Hook KisMimeDatabase::suffixesForMimeType
typedef QStringList (*SuffixesForMimeTypeFn)(const QString&);
static SuffixesForMimeTypeFn orig_suffixesForMimeType = nullptr;

extern "C" QStringList _ZN15KisMimeDatabase19suffixesForMimeTypeERK7QString(const QString& mimeType) {
    if (!orig_suffixesForMimeType) {
        orig_suffixesForMimeType = (SuffixesForMimeTypeFn)dlsym(RTLD_NEXT, "_ZN15KisMimeDatabase19suffixesForMimeTypeERK7QString");
    }
    if (mimeType == "application/x-krita" || mimeType == "application/x-rlstudio") {
        QStringList list;
        list << QStringLiteral("rls") << QStringLiteral("kra");
        return list;
    }
    return orig_suffixesForMimeType ? orig_suffixesForMimeType(mimeType) : QStringList();
}

// 7. Hook KisMimeDatabase::mimeTypeForSuffix
typedef QString (*MimeTypeForSuffixFn)(const QString&);
static MimeTypeForSuffixFn orig_mimeTypeForSuffix = nullptr;

extern "C" QString _ZN15KisMimeDatabase17mimeTypeForSuffixERK7QString(const QString& suffix) {
    if (suffix.compare("rls", Qt::CaseInsensitive) == 0) {
        return QStringLiteral("application/x-krita");
    }
    if (!orig_mimeTypeForSuffix) {
        orig_mimeTypeForSuffix = (MimeTypeForSuffixFn)dlsym(RTLD_NEXT, "_ZN15KisMimeDatabase17mimeTypeForSuffixERK7QString");
    }
    return orig_mimeTypeForSuffix ? orig_mimeTypeForSuffix(suffix) : QString();
}

// 8. Hook KisMimeDatabase::mimeTypeForFile
typedef QString (*MimeTypeForFileFn)(const QString&, bool);
static MimeTypeForFileFn orig_mimeTypeForFile = nullptr;

extern "C" QString _ZN15KisMimeDatabase15mimeTypeForFileERK7QStringb(const QString& file, bool matchMode) {
    if (file.endsWith(".rls", Qt::CaseInsensitive)) {
        return QStringLiteral("application/x-krita");
    }
    if (!orig_mimeTypeForFile) {
        orig_mimeTypeForFile = (MimeTypeForFileFn)dlsym(RTLD_NEXT, "_ZN15KisMimeDatabase15mimeTypeForFileERK7QStringb");
    }
    return orig_mimeTypeForFile ? orig_mimeTypeForFile(file, matchMode) : QString();
}

// 9. Hook KisMimeDatabase::descriptionForMimeType
typedef QString (*DescForMimeTypeFn)(const QString&);
static DescForMimeTypeFn orig_descForMimeType = nullptr;

extern "C" QString _ZN15KisMimeDatabase22descriptionForMimeTypeERK7QString(const QString& mimeType) {
    if (mimeType == "application/x-krita" || mimeType == "application/x-rlstudio") {
        return QStringLiteral("RL Studio belgesi (*.rls)");
    }
    if (!orig_descForMimeType) {
        orig_descForMimeType = (DescForMimeTypeFn)dlsym(RTLD_NEXT, "_ZN15KisMimeDatabase22descriptionForMimeTypeERK7QString");
    }
    return orig_descForMimeType ? orig_descForMimeType(mimeType) : QString();
}

// 10. Hook QMimeDatabase::mimeTypeForFile
typedef QMimeType (*MimeForFileQtFn)(const QMimeDatabase*, const QString&, int);
static MimeForFileQtFn orig_qtMimeForFile = nullptr;

extern "C" QMimeType _ZNK13QMimeDatabase15mimeTypeForFileERK7QStringNS_9MatchModeE(const QMimeDatabase* self, const QString& fileName, int mode) {
    if (!orig_qtMimeForFile) {
        orig_qtMimeForFile = (MimeForFileQtFn)dlsym(RTLD_NEXT, "_ZNK13QMimeDatabase15mimeTypeForFileERK7QStringNS_9MatchModeE");
    }
    if (fileName.endsWith(".rls", Qt::CaseInsensitive)) {
        return self->mimeTypeForName(QStringLiteral("application/x-krita"));
    }
    return orig_qtMimeForFile ? orig_qtMimeForFile(self, fileName, mode) : QMimeType();
}

// 11. Hook QFileDialog::selectFile
typedef void (*SelectFileFn)(QFileDialog*, const QString&);
static SelectFileFn orig_selectFile = nullptr;

extern "C" void _ZN11QFileDialog10selectFileERK7QString(QFileDialog* self, const QString& filename) {
    if (!orig_selectFile) {
        orig_selectFile = (SelectFileFn)dlsym(RTLD_NEXT, "_ZN11QFileDialog10selectFileERK7QString");
    }
    QString f = filename;
    if (f.endsWith(".kra", Qt::CaseInsensitive)) {
        f.chop(4);
        f.append(".rls");
    }
    if (orig_selectFile) {
        orig_selectFile(self, f);
    }
}

// 12. Hook QFileDialog::selectedFiles
typedef QStringList (*SelectedFilesFn)(const QFileDialog*);
static SelectedFilesFn orig_selectedFiles = nullptr;

extern "C" QStringList _ZNK11QFileDialog13selectedFilesEv(const QFileDialog* self) {
    if (!orig_selectedFiles) {
        orig_selectedFiles = (SelectedFilesFn)dlsym(RTLD_NEXT, "_ZNK11QFileDialog13selectedFilesEv");
    }
    QStringList files = orig_selectedFiles ? orig_selectedFiles(self) : QStringList();
    for (int i = 0; i < files.size(); ++i) {
        if (files[i].endsWith(".kra", Qt::CaseInsensitive)) {
            files[i].chop(4);
            files[i].append(".rls");
        } else if (!files[i].contains('.')) {
            files[i].append(".rls");
        }
    }
    return files;
}

// 13. Hook QFileDialog::setDefaultSuffix
typedef void (*SetDefaultSuffixFn)(QFileDialog*, const QString&);
static SetDefaultSuffixFn orig_setDefaultSuffix = nullptr;

extern "C" void _ZN11QFileDialog16setDefaultSuffixERK7QString(QFileDialog* self, const QString& suffix) {
    if (!orig_setDefaultSuffix) {
        orig_setDefaultSuffix = (SetDefaultSuffixFn)dlsym(RTLD_NEXT, "_ZN11QFileDialog16setDefaultSuffixERK7QString");
    }
    QString s = suffix;
    if (s.isEmpty() || s.compare("kra", Qt::CaseInsensitive) == 0) {
        s = QStringLiteral("rls");
    }
    if (orig_setDefaultSuffix) {
        orig_setDefaultSuffix(self, s);
    }
}

// 14. Hook QFileDialog::setNameFilters
typedef void (*SetNameFiltersFn)(QFileDialog*, const QStringList&);
static SetNameFiltersFn orig_setNameFilters = nullptr;

extern "C" void _ZN11QFileDialog14setNameFiltersERK11QStringList(QFileDialog* self, const QStringList& filters) {
    if (!orig_setNameFilters) {
        orig_setNameFilters = (SetNameFiltersFn)dlsym(RTLD_NEXT, "_ZN11QFileDialog14setNameFiltersERK11QStringList");
    }
    QStringList updated = filters;
    for (int i = 0; i < updated.size(); ++i) {
        updated[i].replace(".kra", ".rls");
        updated[i].replace("*.kra", "*.rls");
        updated[i].replace("Krita belgesi", "RL Studio belgesi (*.rls)");
        updated[i].replace("Krita document", "RL Studio document (*.rls)");
        updated[i].replace("Krita Document", "RL Studio Document (*.rls)");
    }
    if (orig_setNameFilters) {
        orig_setNameFilters(self, updated);
    }
}

// 15. Hook QFileDialogOptions::setNameFilters (for Native GNOME Portal File Dialog)
extern "C" void _ZN18QFileDialogOptions14setNameFiltersERK11QStringList(void* self, const QStringList& filters) {
    static auto orig = (void (*)(void*, const QStringList&))dlsym(RTLD_NEXT, "_ZN18QFileDialogOptions14setNameFiltersERK11QStringList");
    QStringList updated = filters;
    for (int i = 0; i < updated.size(); ++i) {
        updated[i].replace(".kra", ".rls");
        updated[i].replace("*.kra", "*.rls");
        updated[i].replace("Krita belgesi", "RL Studio belgesi (*.rls)");
        updated[i].replace("Krita document", "RL Studio document (*.rls)");
        updated[i].replace("Krita Document", "RL Studio Document (*.rls)");
        updated[i].replace("Krita", "RL Studio");
    }
    if (orig) orig(self, updated);
}

// 16. Hook QMessageBox::critical, warning, information
typedef QMessageBox::StandardButton (*MsgBoxFn)(QWidget*, const QString&, const QString&, QMessageBox::StandardButtons, QMessageBox::StandardButton);

extern "C" QMessageBox::StandardButton _ZN11QMessageBox8criticalEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_(
    QWidget* parent, const QString& title, const QString& text, QMessageBox::StandardButtons buttons, QMessageBox::StandardButton defaultButton) {
    static auto orig = (MsgBoxFn)dlsym(RTLD_NEXT, "_ZN11QMessageBox8criticalEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_");
    return orig ? orig(parent, cleanTitle(title), cleanMessage(text), buttons, defaultButton) : QMessageBox::NoButton;
}

extern "C" QMessageBox::StandardButton _ZN11QMessageBox7warningEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_(
    QWidget* parent, const QString& title, const QString& text, QMessageBox::StandardButtons buttons, QMessageBox::StandardButton defaultButton) {
    static auto orig = (MsgBoxFn)dlsym(RTLD_NEXT, "_ZN11QMessageBox7warningEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_");
    return orig ? orig(parent, cleanTitle(title), cleanMessage(text), buttons, defaultButton) : QMessageBox::NoButton;
}

extern "C" QMessageBox::StandardButton _ZN11QMessageBox11informationEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_(
    QWidget* parent, const QString& title, const QString& text, QMessageBox::StandardButtons buttons, QMessageBox::StandardButton defaultButton) {
    static auto orig = (MsgBoxFn)dlsym(RTLD_NEXT, "_ZN11QMessageBox11informationEP7QWidgetRK7QStringS4_6QFlagsINS_14StandardButtonEES6_");
    return orig ? orig(parent, cleanTitle(title), cleanMessage(text), buttons, defaultButton) : QMessageBox::NoButton;
}
