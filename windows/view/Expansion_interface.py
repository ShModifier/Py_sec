from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import QFileDialog, QSizePolicy, QTableWidgetItem, QButtonGroup, QWidget, QVBoxLayout, QLabel, \
    QApplication, QCompleter, QHBoxLayout, QLineEdit,QGridLayout, QGraphicsOpacityEffect
import json,os
from qfluentwidgets import TitleLabel, SearchLineEdit, SwitchButton, StrongBodyLabel, HeaderCardWidget, BodyLabel, TitleLabel, InfoBarPosition,InfoBar,InfoBarIcon, Flyout, PrimaryPushButton, CardWidget, TableWidget, PlainTextEdit, CheckBox, RadioButton,ScrollArea,LineEdit, PushButton, SearchLineEdit, setTheme, Theme
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet
from qfluentwidgets import FluentIcon as FIF, IconWidget
from rules.rule_registry import load_rules

class ExpansionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("expansionInterface")
        self.setStyleSheet("background: transparent;")

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.createIntroductionCard())
        self.mainLayout.setSpacing(15)
        self.mainLayout.setContentsMargins(30, 30, 30, 30)

        #搜索部分
        self.searchLineEdit = SearchLineEdit(self)
        self.searchLineEdit.setPlaceholderText("搜索模块（支持名称/描述）")
        self.searchLineEdit.setFixedWidth(300)
        self.searchLineEdit.textChanged.connect(self.searchExpasion)
        self.mainLayout.addWidget(self.searchLineEdit)

        #拓展模块

        self.rule_widgets = []
        self.mainLayout.addWidget(self.initExpansionLayout())

        #按钮


        self.ButtonLayout = QHBoxLayout(self)
        self.openAllButton = PrimaryPushButton('全部启用')
        self.closeAllButton = PrimaryPushButton('全部禁用')
        self.saveConfigButton = PrimaryPushButton('保存配置')

        self.openAllButton.clicked.connect(self.openAllPart)
        self.closeAllButton.clicked.connect(self.closeAllPart)
        self.saveConfigButton.clicked.connect(self.save_config)

        self.ButtonLayout.addWidget(self.openAllButton)
        self.ButtonLayout.addWidget(self.closeAllButton)
        self.ButtonLayout.addWidget(self.saveConfigButton)

        self.mainLayout.addLayout(self.ButtonLayout)





    def createIntroductionCard(self):
        mainLayout = QVBoxLayout(self)

        titleLabel = TitleLabel("模块管理")
        detailednLabel=BodyLabel("在当前页面可以查看和管理目前已有的漏洞模块，通过模块右侧的按钮启用或禁用模块")
        addLabel = BodyLabel("如想要添加自定义模块，请按照官方文档中的步骤进行添加注册")
        mainLayout.addWidget(titleLabel)
        mainLayout.addWidget(detailednLabel)
        mainLayout.addWidget(addLabel)

        return mainLayout

    def createExpansionLayout(self, rule,config):
        expansionCard = CardWidget(self)
        expansionCard.setMinimumHeight(80)
        expansionCard.setMaximumHeight(80)

        mainLayout = QHBoxLayout(expansionCard)


        leftLayout = QVBoxLayout()

        expansionTitleLabel = StrongBodyLabel(rule.name)
        descLabel = BodyLabel(rule.description)

        leftLayout.addWidget(expansionTitleLabel)
        leftLayout.addWidget(descLabel)

        button=SwitchButton()

        button.setChecked(config.get(rule.id, True))
        if config.get(rule.id, True):
            self.setCardOpacity(expansionCard, 1.0)
        else:
            self.setCardOpacity(expansionCard, 0.4)

        button.setOffText("禁用")
        button.setOnText("启用")

        def onToggle(checked):

            if checked:
                self.setCardOpacity(expansionCard, 1.0)
                rule.enabled = True

            else:
                self.setCardOpacity(expansionCard, 0.4)
                rule.enabled = False


        button.checkedChanged.connect(onToggle)
        self.rule_widgets.append((rule, button, expansionCard))

        mainLayout.addLayout(leftLayout)
        mainLayout.addStretch()
        mainLayout.addWidget(button)

        return expansionCard

    def setCardOpacity(self, card, value):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(value)
        card.setGraphicsEffect(effect)

    def save_config(self):
        config_path = "tools_config.json"

        # 读取已有配置
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except:
                config = {}
        else:
            config = {}

        # 更新 rules 部分
        config["rules"] = {rule.id: rule.enabled for rule in self.rules}

        # 写回
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        self.saveSuccess()

    def load_config(self):
        config_path = "tools_config.json"

        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("rules", {})
        except json.JSONDecodeError:
            return {}

    def initExpansionLayout(self):
        expansionArea = ScrollArea(self)
        expansionWidget = QWidget()

        expansionLayout = QVBoxLayout(expansionWidget)

        expansionLayout.setSpacing(5)
        expansionLayout.setContentsMargins(20, 20, 20, 20)


        self.rules = load_rules()
        config = self.load_config()

        for rule in self.rules:
            card = self.createExpansionLayout(rule,config)
            card.setStyleSheet("background: transparent;")
            expansionLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            expansionLayout.addWidget(card)

        expansionArea.setWidget(expansionWidget)
        expansionArea.setWidgetResizable(True)

        return expansionArea

    def saveSuccess(self):
        InfoBar.success(
            title='保存成功',
            content="下次保存前将保持当前配置进行检查",
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self,
        )
    def openAllSuccess(self):
        InfoBar.success(
            title='启用成功',
            content="所有模块均已启用",
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self,
        )

    def closeAllSuccess(self):
        InfoBar.success(
            title='禁用成功',
            content="所有模块均已禁用，当前仅能进行AI辅助检查分析",
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self,
        )

    def openAllPart(self):
        for rule, button, card in self.rule_widgets:
            rule.enabled = True
            button.setChecked(True)

        self.openAllSuccess()

    def closeAllPart(self):
        for rule, button, card in self.rule_widgets:
            rule.enabled = False
            button.setChecked(False)

        self.closeAllSuccess()

    def searchExpasion(self, text: str):
        keyword = text.lower().strip()

        for rule, button, card in self.rule_widgets:
            # 拼接可搜索内容
            content = f"{rule.name} {rule.description}".lower()

            if keyword == "" or keyword in content:
                card.show()
            else:
                card.hide()

