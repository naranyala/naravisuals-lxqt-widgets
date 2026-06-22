#include <QWidget>
#include <QDialog>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QComboBox>
#include <QPushButton>
#include <QDBusConnection>
#include <QDBusInterface>
#include <QDBusReply>
#include <QDBusAbstractAdaptor>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QTimer>
#include <QDebug>
#include <QBoxLayout>

#include <ilxqtpanelplugin.h>
#include <pluginsettings.h>

static const QString BUS_NAME = "org.naravisuals.Daemon";
static const QString OBJ_PATH = "/org/naravisuals/Daemon";
static const QString IFACE_NAME = "org.naravisuals.Daemon";

static QStringList allWidgets()
{
    return {
        "system-monitor", "weather", "quick-notes", "clipboard-manager",
        "pomodoro", "network-monitor", "tray-enhanced", "media-player", "battery"
    };
}

// --- Renderer base class ---
class WidgetRenderer : public QWidget
{
    Q_OBJECT
public:
    explicit WidgetRenderer(QWidget *parent = nullptr) : QWidget(parent) {}
    virtual void updateData(const QJsonObject &data) = 0;
};

// --- Text renderer (kernel, uptime, ping) ---
class TextRenderer : public WidgetRenderer
{
    Q_OBJECT
public:
    explicit TextRenderer(QWidget *parent = nullptr) : WidgetRenderer(parent)
    {
        _label = new QLabel(this);
        _label->setAlignment(Qt::AlignCenter);
        _label->setStyleSheet("color: #ccc; font-size: 11px;");
        QVBoxLayout *lay = new QVBoxLayout(this);
        lay->setContentsMargins(4, 2, 4, 2);
        lay->addWidget(_label);
    }

    void updateData(const QJsonObject &data) override
    {
        // Try common keys
        for (const QString &key : {"formatted", "kernel", "host", "description", "temp_c"})
        {
            if (data.contains(key))
            {
                QString text = data[key].toString();
                if (key == "temp_c" && text != "--")
                    text += " C";
                _label->setText(text);
                return;
            }
        }
        _label->setText(QJsonDocument(data).toJson(QJsonDocument::Compact));
    }

private:
    QLabel *_label;
};

// --- Bar renderer (CPU, RAM, disk usage) ---
class BarRenderer : public WidgetRenderer
{
    Q_OBJECT
public:
    explicit BarRenderer(QWidget *parent = nullptr) : WidgetRenderer(parent)
    {
        setMinimumHeight(18);
        setMaximumHeight(18);
    }

    void setLabel(const QString &label) { _label = label; }
    void setColor(const QColor &color) { _color = color; }

    void updateData(const QJsonObject &data) override
    {
        QString key = _label.toLower() + "_percent";
        _value = data.value(key).toDouble();
        update();
    }

protected:
    void paintEvent(QPaintEvent *) override
    {
        QPainter p(this);
        int w = width(), h = height();
        p.fillRect(0, 0, w, h, QColor(40, 40, 40));
        int fill = int(w * _value / 100.0);
        p.fillRect(0, 0, fill, h, _color);
        p.setPen(QColor(200, 200, 200));
        p.drawText(4, 0, w - 4, h, Qt::AlignVCenter,
                   QString("%1: %2%").arg(_label).arg(_value, 0, 'f', 1));
    }

private:
    QString _label;
    QColor _color = Qt::green;
    double _value = 0;
};

// --- Composite renderer (system monitor with multiple bars) ---
class SystemMonitorRenderer : public WidgetRenderer
{
    Q_OBJECT
public:
    explicit SystemMonitorRenderer(QWidget *parent = nullptr) : WidgetRenderer(parent)
    {
        QHBoxLayout *lay = new QHBoxLayout(this);
        lay->setContentsMargins(0, 0, 0, 0);
        lay->setSpacing(4);

        _cpuBar = new BarRenderer(this);
        _cpuBar->setLabel("CPU");
        _cpuBar->setColor(QColor(46, 204, 113));

        _ramBar = new BarRenderer(this);
        _ramBar->setLabel("RAM");
        _ramBar->setColor(QColor(52, 152, 219));

        _diskBar = new BarRenderer(this);
        _diskBar->setLabel("DISK");
        _diskBar->setColor(QColor(155, 89, 182));

        _swapBar = new BarRenderer(this);
        _swapBar->setLabel("SWAP");
        _swapBar->setColor(QColor(231, 76, 60));

        _netLabel = new QLabel("NET: ?", this);
        _netLabel->setStyleSheet("color: #aaa; font-size: 10px;");

        lay->addWidget(_cpuBar);
        lay->addWidget(_ramBar);
        lay->addWidget(_diskBar);
        lay->addWidget(_swapBar);
        lay->addWidget(_netLabel);
    }

    void updateData(const QJsonObject &data) override
    {
        _cpuBar->updateData(data);
        _ramBar->updateData(data);
        _diskBar->updateData(data);
        _swapBar->updateData(data);
        if (data.contains("net_rate"))
            _netLabel->setText("NET: " + data["net_rate"].toString());
    }

private:
    BarRenderer *_cpuBar, *_ramBar, *_diskBar, *_swapBar;
    QLabel *_netLabel;
};

// --- Icon+Text renderer (weather, battery) ---
class IconTextRenderer : public WidgetRenderer
{
    Q_OBJECT
public:
    explicit IconTextRenderer(QWidget *parent = nullptr) : WidgetRenderer(parent)
    {
        QHBoxLayout *lay = new QHBoxLayout(this);
        lay->setContentsMargins(4, 2, 4, 2);
        lay->setSpacing(6);

        _iconLabel = new QLabel(this);
        _iconLabel->setStyleSheet("font-size: 16px;");
        _textLabel = new QLabel(this);
        _textLabel->setStyleSheet("color: #ccc; font-size: 10px;");

        lay->addWidget(_iconLabel);
        lay->addWidget(_textLabel);
        lay->addStretch();
    }

    void setIconChar(const QString &ch) { _iconLabel->setText(ch); }

    void updateData(const QJsonObject &data) override
    {
        // Flexible: show first text-like value
        QString text;
        for (auto it = data.begin(); it != data.end(); ++it)
        {
            if (it.value().isString() && !it.value().toString().isEmpty())
            {
                text = it.value().toString();
                break;
            }
        }
        _textLabel->setText(text);
    }

private:
    QLabel *_iconLabel;
    QLabel *_textLabel;
};

// --- Main plugin class ---
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
    void onDataUpdated(const QString &widgetId, const QString &jsonData);
    void onRequestData();

private:
    QWidget *mWidget = nullptr;
    QWidget *mContainer = nullptr;
    QDBusInterface *mDBus = nullptr;
    QString mSelectedWidget;
    WidgetRenderer *mRenderer = nullptr;
    QTimer *mPollTimer = nullptr;
    bool mIsGeneric = false;

    void startWidget();
    void stopWidget();
    WidgetRenderer *createRenderer(const QString &widgetId);
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
    // Detect widget from library name (e.g. libnaravisuals-system-monitor.so)
    QFileInfo fi(QString::fromLocal8Bit(dladdr ? "" : ""));
    mSelectedWidget = settings()->value("widget", "system-monitor").toString();
    mIsGeneric = settings()->value("generic", true).toBool();

    mContainer = new QWidget();
    QVBoxLayout *lay = new QVBoxLayout(mContainer);
    lay->setContentsMargins(0, 0, 0, 0);
    mWidget = mContainer;

    // Connect to D-Bus daemon
    mDBus = new QDBusInterface(BUS_NAME, OBJ_PATH, IFACE_NAME, QDBusConnection::sessionBus(), this);

    if (mDBus->isValid())
    {
        // Subscribe to data updates
        QDBusConnection::sessionBus().connect(
            BUS_NAME, OBJ_PATH, IFACE_NAME, "dataUpdated",
            this, SLOT(onDataUpdated(QString, QString)));
    }

    // Poll timer as fallback (D-Bus signals may not always work)
    mPollTimer = new QTimer(this);
    connect(mPollTimer, &QTimer::timeout, this, &NaraVisualsPlugin::requestData);
    mPollTimer->start(2000);

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
    if (mRenderer)
        return;

    mRenderer = createRenderer(mSelectedWidget);
    if (!mRenderer)
    {
        QLabel *err = new QLabel("No renderer for: " + mSelectedWidget, mContainer);
        err->setStyleSheet("color: red; font-size: 9px;");
        mContainer->layout()->addWidget(err);
        return;
    }

    mContainer->layout()->addWidget(mRenderer);

    // Initial data request
    requestData();
}

void NaraVisualsPlugin::stopWidget()
{
    mPollTimer->stop();
    if (mRenderer)
    {
        mContainer->layout()->removeWidget(mRenderer);
        mRenderer->deleteLater();
        mRenderer = nullptr;
    }
}

WidgetRenderer *NaraVisualsPlugin::createRenderer(const QString &widgetId)
{
    if (widgetId == "system-monitor")
        return new SystemMonitorRenderer(mContainer);
    if (widgetId == "weather" || widgetId == "battery")
    {
        auto *r = new IconTextRenderer(mContainer);
        r->setIconChar(widgetId == "weather" ? "\u2601" : "\U0001F50B");
        return r;
    }
    // Default: text renderer for all others
    return new TextRenderer(mContainer);
}

void NaraVisualsPlugin::requestData()
{
    if (!mDBus || !mDBus->isValid())
        return;

    QDBusReply<QString> reply = mDBus->call("GetData", mSelectedWidget);
    if (!reply.isValid())
        return;

    QJsonDocument doc = QJsonDocument::fromJson(reply.value().toUtf8());
    if (doc.isObject())
        onDataUpdated(mSelectedWidget, reply.value());
}

void NaraVisualsPlugin::onDataUpdated(const QString &widgetId, const QString &jsonData)
{
    if (widgetId != mSelectedWidget || !mRenderer)
        return;

    QJsonDocument doc = QJsonDocument::fromJson(jsonData.toUtf8());
    if (doc.isObject())
        mRenderer->updateData(doc.object());
}

#include "naravisuals-plugin.moc"
