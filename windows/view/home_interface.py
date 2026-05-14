# coding:utf-8
from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import InfoBarPosition, HeaderCardWidget, InfoBar, EditableComboBox, HyperlinkLabel, LargeTitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, ComboBox, CardWidget, PasswordLineEdit, ScrollArea, isDarkTheme, FluentIcon, PrimaryPushButton,LineEdit, PushButton, SearchLineEdit, setTheme, Theme
from ..common.icon import FluentIconBase
from qfluentwidgets import FluentIcon as FIF, IconWidget
from app.config_manager import save_api_config, get_api_config



class HomeInterface(QWidget):
    switchToAudit = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("homeInterface")
        self.setStyleSheet("background: transparent;")

        # 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setSpacing(15)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)

        # ===== 标题 =====
        self.titleCard=CardWidget()
        self.titleLayout = QHBoxLayout(self.titleCard)
        self.titleLayout.setContentsMargins(20, 20, 20, 20)
        self.titleLayout.setSpacing(15)

        self.titleLayout.addLayout(
            self.createTitleLayout(
                ":/gallery/images/logo.png",
                "Pysec_Audit",
                "支持漏洞规则的扩展与自定义，同时提供可视化界面，实现代码上传、自动扫描、结果展示与修复建议一体化流程。适用于多种 Python Web 应用场景。"
            )
        )
        self.mainLayout.addWidget(self.titleCard)


        # ===== 基础配置卡片 =====
        self.baseCard = HeaderCardWidget()

        self.baseLayout = QVBoxLayout()
        self.baseCard.setTitle("基础配置")
        self.baseCard.viewLayout.addLayout(self.baseLayout)

        self.platformBox = ComboBox()
        self.platformBox.addItems(["DeepSeek", "通义千问（Qwen）","OpenAI"])
        self.platformBox.currentTextChanged.connect(self.onPlatformChanged)
        self.baseLayout.addLayout(
            self.createSettingItem(
                FIF.GLOBE,
                "Service Platform",
                "请选择你需要使用的模型服务平台",
                self.platformBox
            )
        )

        self.mainLayout.addWidget(self.baseCard)

        # ===== API 配置卡片 =====
        self.apiStack = QStackedWidget()

        self.apiStack.addWidget(self.deepseekApiCard())
        self.apiStack.addWidget(self.tongyiApiCard())
        self.apiStack.addWidget(self.openaiApiCard())

        self.mainLayout.addWidget(self.apiStack)

        # ===== 操作按钮 =====
        #btnLayout = QHBoxLayout()

        self.saveButton = PrimaryPushButton("保存配置")
        self.startButton = PrimaryPushButton("开始扫描")

        self.mainLayout.addLayout(
            self.createSaveLayout(
                ":/gallery/images/logo.png",
                "使用ai辅助语义分析扫描前请点击按钮进行保存👉🏼",
                self.saveButton, self.startButton
            )
        )
        self.load_api_info()
        self.saveButton.clicked.connect(self.save_api_info)
        self.startButton.clicked.connect(self.switchToAudit.emit)




        # 底部弹性空间
        self.mainLayout.addStretch()

    def createTitleLayout(self, icon, title, desc):
        """一行”左侧logo+右侧文本和控件"""
        mainLayout = QHBoxLayout()

        # ===== 左侧（icon）=====
        iconWidget = IconWidget(icon, self)
        iconWidget.setFixedSize(60, 60)
        mainLayout.addWidget(iconWidget)

        #===== 纵向布局：右侧大标题+详细介绍+链接(横向)=====
        rightLayout = QVBoxLayout()

        titleLabel = LargeTitleLabel(title)
        descLabel = BodyLabel(desc)
        descLabel.setWordWrap(True)  #这是自动换行

        linkLayout = QHBoxLayout()
        startLink = HyperlinkLabel("快速开始")
        startLink.setUrl("https://github.com/ShModifier/Py_sec/blob/main/README.md")
        repoLink = HyperlinkLabel("反馈")
        repoLink.setUrl("https://github.com/ShModifier/Py_sec/issues")
        codeLink = HyperlinkLabel("源码")
        codeLink.setUrl("https://github.com/ShModifier/")
        linkLayout.addWidget(startLink)
        linkLayout.addWidget(repoLink)
        linkLayout.addWidget(codeLink)


        rightLayout.addWidget(titleLabel)
        rightLayout.addWidget(descLabel)
        rightLayout.addLayout(linkLayout)

        mainLayout.addLayout(rightLayout)

        return mainLayout




    def createSettingItem(self, icon, title, desc, widget):
        """ 创建一行：左文本 + 右控件 """

        mainLayout = QHBoxLayout()
        # ===== 左侧（icon + 文字）=====
        leftLayout = QHBoxLayout()

        # icon
        iconWidget = IconWidget(icon, self)
        iconWidget.setFixedSize(20, 20)

        # 文字（上下）
        textLayout = QVBoxLayout()
        titleLabel = StrongBodyLabel(title)


        descLabel = BodyLabel(desc)

        textLayout.addWidget(titleLabel)
        textLayout.addWidget(descLabel)

        leftLayout.addWidget(iconWidget)
        leftLayout.addLayout(textLayout)
        leftLayout.setSpacing(10)

        # ===== 右侧控件 =====
        widget.setFixedHeight(32)
        widget.setMinimumWidth(200)

        # ===== 组合 =====
        mainLayout.addLayout(leftLayout)
        mainLayout.addStretch()
        mainLayout.addWidget(widget)

        return mainLayout

    def createSaveLayout(self, icon, text, *widgets):
        layout = QHBoxLayout()

        leftLayout = QHBoxLayout()

        # icon
        iconLabel = BodyLabel()
        pixmap = QPixmap(icon).scaled(20, 20)
        iconLabel.setPixmap(pixmap)
        iconLabel.setFixedWidth(30)

        textLabel =BodyLabel(text)


        leftLayout.addWidget(iconLabel)
        leftLayout.addWidget(textLabel)

        layout.addLayout(leftLayout)
        layout.addStretch()

        for w in widgets:
            layout.addWidget(w)

        return layout

    def onPlatformChanged(self, text):
        mapping = {
            "DeepSeek": 0,
            "通义千问（Qwen）": 1,
            "OpenAI": 2
        }
        self.apiStack.setCurrentIndex(mapping.get(text, 0))

    def deepseekApiCard(self):
        apiCard = HeaderCardWidget()
        apiCard.setTitle("API 配置")
        apiCard.viewLayout.setContentsMargins(0, 0, 0, 0)

        apiLayout = QVBoxLayout()
        apiCard.viewLayout.addLayout(apiLayout)

        apiLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        apiLayout.setContentsMargins(20, 20, 20, 20)
        apiLayout.setSpacing(15)

        self.DSmodelInput = EditableComboBox()
        self.items = ['deepseek-chat', 'deepseek-reasoner']
        self.DSmodelInput.addItems(self.items)
        self.DSmodelInput.setPlaceholderText("输入或选择要使用的大模型")

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.TILES,
                "Model",
                "输入或选择要使用的大模型",
                self.DSmodelInput
            )
        )

        self.DSApiInput = LineEdit()
        self.DSApiInput.setPlaceholderText("https://api.deepseek.com")

        self.DSKeyInput = PasswordLineEdit()
        self.DSKeyInput.setPlaceholderText("请输入 API KEY")

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.CLOUD,
                "API URL",
                "服务接口地址(默认为官方文档所提供地址，可修改)",
                self.DSApiInput
            )
        )

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.VPN,
                "API KEY",
                "用于身份认证的密钥",
                self.DSKeyInput
            )
        )
        return apiCard

    def tongyiApiCard(self):
        apiCard = HeaderCardWidget()
        apiCard.setTitle("API 配置")
        apiCard.viewLayout.setContentsMargins(0, 0, 0, 0)

        apiLayout = QVBoxLayout()
        apiCard.viewLayout.addLayout(apiLayout)

        apiLayout.setContentsMargins(20, 20, 20, 20)
        apiLayout.setSpacing(15)
        apiLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.QWmodelInput = EditableComboBox()
        self.items= ['Qwen3', 'Qwen3.5-Flash','Qwen3-Max', 'Qwen3.5-Plus']
        self.QWmodelInput.addItems(self.items)
        self.QWmodelInput.setPlaceholderText("输入或选择要使用的大模型")

        #self.modelInput.currentIndexChanged.connect()  #接收信号，待补全


        self.QWApiInput = LineEdit()
        self.QWApiInput.setPlaceholderText("https://dashscope.aliyuncs.com/compatible-mode/v1")

        self.QWKeyInput = PasswordLineEdit()
        self.QWKeyInput.setPlaceholderText("请输入 API KEY")

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.TILES,
                "Model",
                "输入或选择要使用的大模型",
                self.QWmodelInput
            )
        )

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.CLOUD,
                "API URL",
                "服务接口地址(默认为官方文档所提供地址，可修改）",
                self.QWApiInput
            )
        )

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.VPN,
                "API KEY",
                "用于身份认证的密钥",
                self.QWKeyInput
            )
        )
        return apiCard

    def openaiApiCard(self):
        apiCard = HeaderCardWidget()
        apiCard.setTitle("API 配置")
        apiCard.viewLayout.setContentsMargins(0, 0, 0, 0)

        apiLayout = QVBoxLayout()
        apiCard.viewLayout.addLayout(apiLayout)

        apiLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        apiLayout.setContentsMargins(20, 20, 20, 20)
        apiLayout.setSpacing(15)

        self.OpenmodelInput = EditableComboBox()
        self.items = ['gpt-5.5','gpt-5.4', 'gpt-5.4-mini']
        self.OpenmodelInput.addItems(self.items)
        self.OpenmodelInput.setPlaceholderText("输入或选择要使用的大模型")

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.TILES,
                "Model",
                "输入或选择要使用的大模型",
                self.OpenmodelInput
            )
        )

        self.OpenKeyInput = PasswordLineEdit()
        self.OpenKeyInput.setPlaceholderText("请输入 API KEY")

        apiLayout.addLayout(
            self.createSettingItem(
                FIF.VPN,
                "API KEY",
                "用于身份认证的密钥",
                self.OpenKeyInput
            )
        )
        return apiCard

    def save_api_info(self):
        platform = self.platformBox.currentText()

        if platform == "DeepSeek":
            api_config = {
                "provider": platform,
                "api_key": self.DSKeyInput.text(),
                "base_url": self.DSApiInput.text(),
                "model": self.DSmodelInput.text(),
            }
        elif platform == "通义千问（Qwen）":
            api_config = {
                "provider": platform,
                "api_key": self.QWKeyInput.text(),
                "base_url": self.QWApiInput.text(),
                "model": self.QWmodelInput.text(),
            }


        elif platform == "OpenAI":
            api_config = {
                "provider": platform,
                "api_key": self.OAKeyInput.text(),
                "base_url": "",
                "model": self.OAModelInput.text(),
            }

        try:
            save_api_config(api_config)
            self.successSaveInfo()
        except Exception as e:
            print("保存失败:", e)


    def successSaveInfo(self):
        InfoBar.success(
            title='API配置已保存！',
            content="直到下次更新API信息前将一直使用当前信息",
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,
            parent=self
        )

    def load_api_info(self):
        config = get_api_config()
        provider = config.get("provider", "DeepSeek")
        # 切换 UI
        index = self.platformBox.findText(provider)
        if index != -1:
            self.platformBox.setCurrentIndex(index)
        # 根据 provider 写入对应 UI
        if provider == "DeepSeek":
            self.DSKeyInput.setText(config.get("api_key", ""))
            self.DSApiInput.setText(config.get("base_url", ""))
            self.DSmodelInput.setText(config.get("model", ""))
        elif provider == "通义千问（Qwen）":
            self.QWKeyInput.setText(config.get("api_key", ""))
            self.QWApiInput.setText(config.get("base_url", ""))
            self.QWmodelInput.setText(config.get("model", ""))
        elif provider == "OpenAI":
            self.OAKeyInput.setText(config.get("api_key", ""))
            self.OAModelInput.setText(config.get("model", ""))