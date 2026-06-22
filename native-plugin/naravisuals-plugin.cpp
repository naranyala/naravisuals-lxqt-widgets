#include <QWidget>
#include <QDialog>
#include <QVBoxLayout>
#include <QLabel>
#include <QComboBox>
#include <QPushButton>
#include <QProcess>
#include <QWindow>
#include <QDebug>
#include <QTimer>
#include <QDir>
#include <QFileInfo>
#include <QLibrary>
#include <dlfcn.h>

#include <ilxqtpanelplugin.h>
#include <pluginsettings.h>

// Force liblxqt.so.2 into NEEDED entries
#include <LXQt/lxqttranslator.h>

static QString detectWidgetFromLibName()
{
    Dl_info info;
    if (dladdr((void*)detectWidgetFromLibName, &info) && info.dli_fname)
    {
        QFileInfo fi(info.dli_fname);
        QString base = fi.baseName();
        if (base.startsWith("lib"))
            base = base.mid(3);
        if (base == "naravisuals")
            return QString();
        QString prefix = "naravisuals-";
        if (base.startsWith(prefix))
            return base.mid(prefix.length());
    }
    return QString();
}

static QStringList allWidgets()
{
    return {
        "system-monitor", "weather", "quick-notes", "clipboard-manager",
        "pomodoro", "network-monitor", "tray-enhanced", "media-player", "battery"
    };
}

class NaraVisualsPlugin : public QObject, public ILXQtPanelPlugin
{
    Q_OBJECT

public:
    NaraVisualsPlugin(const ILXQtPanelPluginStartupInfo &info);
    ~NaraVisualsPlugin() override;

    QWidget *widget() override { return mWidget; }
    QString themeId() const override { return QStringLiteral("NaraVisuals"); }
    Flags flags() const override;
    QDialog *configureDialog() override;

private slots:
    void onProcessReadyRead();
    void onProcessFinished(int exitCode, QProcess::ExitStatus status);
    void startWidget();
    void stopWidget();

private:
    QWidget *mWidget = nullptr;
    QWidget *mContainer = nullptr;
    QProcess *mProcess = nullptr;
    QString mSelectedWidget;
    QWindow *mEmbeddedWindow = nullptr;
    bool mIsGeneric = false;
};

class NaraVisualsPluginLibrary : public QObject, public ILXQtPanelPluginLibrary
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "lxqt.org/Panel/PluginInterface/3.0")
    Q_INTERFACES(ILXQtPanelPluginLibrary)

public:
    ILXQtPanelPlugin *instance(const ILXQtPanelPluginStartupInfo &info) const override
    {
        return new NaraVisualsPlugin(info);
    }
};

// --------------------------------------------------------

NaraVisualsPlugin::NaraVisualsPlugin(const ILXQtPanelPluginStartupInfo &info)
    : QObject(nullptr)
    , ILXQtPanelPlugin(info)
{
    QString detected = detectWidgetFromLibName();
    mIsGeneric = detected.isEmpty();

    if (mIsGeneric)
        mSelectedWidget = settings()->value("widget", "system-monitor").toString();
    else
        mSelectedWidget = detected;

    mContainer = new QWidget();
    QVBoxLayout *lay = new QVBoxLayout(mContainer);
    lay->setContentsMargins(0, 0, 0, 0);
    QLabel *label = new QLabel("Starting...");
    label->setAlignment(Qt::AlignCenter);
    label->setStyleSheet("color: #888; font-size: 10px;");
    lay->addWidget(label);
    mWidget = mContainer;

    LXQt::Translator::translatePlugin(mSelectedWidget, QStringLiteral("naravisuals"));

    startWidget();
}

NaraVisualsPlugin::~NaraVisualsPlugin()
{
    stopWidget();
    delete mContainer;
}

ILXQtPanelPlugin::Flags NaraVisualsPlugin::flags() const
{
    return mIsGeneric ? Flags(HaveConfigDialog) : NoFlags;
}

QDialog *NaraVisualsPlugin::configureDialog()
{
    if (!mIsGeneric)
        return nullptr;

    QDialog *dlg = new QDialog();
    dlg->setWindowTitle("NaraVisuals Widget");

    QVBoxLayout *layout = new QVBoxLayout(dlg);
    QLabel *info = new QLabel("Select widget:");
    layout->addWidget(info);

    QComboBox *combo = new QComboBox();
    for (const QString &w : allWidgets())
    {
        QString label = w;
        combo->addItem(label.replace('-', ' '), w);
    }

    int idx = combo->findData(mSelectedWidget);
    if (idx >= 0)
        combo->setCurrentIndex(idx);
    layout->addWidget(combo);

    QPushButton *ok = new QPushButton("OK");
    connect(ok, &QPushButton::clicked, dlg, &QDialog::accept);
    layout->addWidget(ok);

    if (dlg->exec() == QDialog::Accepted)
    {
        QString newWidget = combo->currentData().toString();
        if (newWidget != mSelectedWidget)
        {
            mSelectedWidget = newWidget;
            settings()->setValue("widget", mSelectedWidget);
            settings()->sync();
            stopWidget();
            startWidget();
        }
    }
    dlg->deleteLater();
    return nullptr;
}

void NaraVisualsPlugin::startWidget()
{
    if (mProcess)
        return;

    if (mSelectedWidget.isEmpty() || !allWidgets().contains(mSelectedWidget))
    {
        qWarning("NaraVisuals: No valid widget selected");
        return;
    }

    QStringList env = QProcess::systemEnvironment();
    QString home = QDir::homePath();
    env << QString("PYTHONPATH=%1/.local/bin/naravisuals:%2/.local/lib/python3.14/site-packages").arg(home).arg(home);

    mProcess = new QProcess(this);
    mProcess->setEnvironment(env);
    mProcess->setProcessChannelMode(QProcess::MergedChannels);

    connect(mProcess, &QProcess::readyReadStandardOutput,
            this, &NaraVisualsPlugin::onProcessReadyRead);
    connect(mProcess,
            QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &NaraVisualsPlugin::onProcessFinished);

    mProcess->start("python3", {
        "-m", "naravisuals.widgets", mSelectedWidget, "--embed"
    });

    if (!mProcess->waitForStarted(3000))
    {
        qWarning("NaraVisuals: Failed to start Python process");
        QLabel *err = new QLabel("Failed to start");
        err->setStyleSheet("color: red; font-size: 9px;");
        mContainer->layout()->addWidget(err);
        return;
    }
}

void NaraVisualsPlugin::stopWidget()
{
    if (mEmbeddedWindow)
    {
        QLayout *lay = mContainer->layout();
        if (lay)
        {
            QLayoutItem *item;
            while ((item = lay->takeAt(0)))
            {
                if (item->widget()) item->widget()->deleteLater();
                delete item;
            }
        }
        mEmbeddedWindow->destroy();
        delete mEmbeddedWindow;
        mEmbeddedWindow = nullptr;
    }
    if (mProcess)
    {
        mProcess->kill();
        mProcess->waitForFinished(2000);
        delete mProcess;
        mProcess = nullptr;
    }
}

void NaraVisualsPlugin::onProcessReadyRead()
{
    QByteArray data = mProcess->readAllStandardOutput();
    QString output = QString::fromUtf8(data).trimmed();
    qDebug() << "NaraVisuals:" << output;

    if (!output.contains("WID:"))
        return;

    int start = output.indexOf("WID:") + 4;
    int end = output.indexOf('\n', start);
    if (end < 0) end = output.length();
    QString widStr = output.mid(start, end - start).trimmed();
    bool ok = false;
    WId wid = widStr.toULongLong(&ok, 16);
    if (!ok || !wid)
        return;

    qDebug() << "NaraVisuals: Embedding WId" << widStr;

    QLayout *lay = mContainer->layout();
    QLayoutItem *item;
    while ((item = lay->takeAt(0)))
    {
        if (item->widget()) item->widget()->deleteLater();
        delete item;
    }

    mEmbeddedWindow = QWindow::fromWinId(wid);
    if (!mEmbeddedWindow)
    {
        QLabel *err = new QLabel("Embed failed");
        err->setStyleSheet("color: red; font-size: 9px;");
        lay->addWidget(err);
        return;
    }

    QWidget *embedded = QWidget::createWindowContainer(mEmbeddedWindow);
    embedded->setMinimumSize(16, 16);
    lay->addWidget(embedded);
}

void NaraVisualsPlugin::onProcessFinished(int exitCode, QProcess::ExitStatus status)
{
    qDebug() << "NaraVisuals: Process exited" << exitCode << status;
    if (status == QProcess::CrashExit)
        QTimer::singleShot(2000, this, &NaraVisualsPlugin::startWidget);
}

#include "naravisuals-plugin.moc"
