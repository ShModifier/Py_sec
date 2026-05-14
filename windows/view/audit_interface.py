import os
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import  QFileDialog, QSizePolicy, QTableWidgetItem, QButtonGroup, QWidget, QVBoxLayout, QLabel, QApplication, QCompleter, QHBoxLayout

from qfluentwidgets import BodyLabel,SwitchButton,InfoBarPosition,InfoBar,InfoBarIcon, Flyout, PrimaryPushButton, CardWidget, TableWidget, PlainTextEdit, CheckBox, RadioButton,ScrollArea,LineEdit, PushButton, SearchLineEdit, setTheme, Theme
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
from ..common.style_sheet import StyleSheet
from app.controller import ScanController
from qfluentwidgets import FluentIcon as FIF, IconWidget
from app.config_manager import get_api_config

class AuditInterface(QWidget):
    def __init__(self, parent=None):
        self.auditResults = {}
        self.controller = ScanController()

        super().__init__(parent)

        self.setObjectName("auditInterface")
        self.setStyleSheet("background: transparent;")

        # ===== Scroll 容器 =====
        #self.scrollWidget = QWidget()
        #self.scrollWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        #.setWidget(self.scrollWidget)
        #self.setWidgetResizable(True)

        #self.mainLayout = QHBoxLayout(self.scrollWidget)
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setSpacing(15)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # ===== 左侧选项卡 =====

        self.leftLayout = QVBoxLayout()

        '''功能选择'''
        self.selectCard = CardWidget()
        self.functionSelection = QHBoxLayout(self.selectCard)

        self.staticAudit = CheckBox("静态审计")
        self.aiAudit = CheckBox("AI语义分析")

        self.staticAudit.stateChanged.connect(self.checkOptiLayout)
        self.aiAudit.stateChanged.connect(self.checkOptiLayout)


        self.functionSelection.addWidget(self.staticAudit)
        self.functionSelection.addWidget(self.aiAudit)

        self.leftLayout.addWidget(self.selectCard)

        self.optiWidget = QWidget()
        self.optiLayout = QHBoxLayout(self.optiWidget)

        self.optiLabel = BodyLabel("使用静态结果优化AI分析")

        self.optiButton = SwitchButton()
        self.optiButton.setChecked(True)
        self.optiButton.setOffText("关闭")
        self.optiButton.setOnText("开启")

        self.optiLayout.addWidget(self.optiLabel)
        self.optiLayout.addStretch()
        self.optiLayout.addWidget(self.optiButton)

        self.optiWidget.hide()

        self.leftLayout.addWidget(self.optiWidget)


        '''单文件/多文件选择'''
        '''
        self.fileCard = CardWidget()
        self.fileChoice = QHBoxLayout(self.fileCard)
        self.singleFile = RadioButton('单文件')
        self.multipleFiles = RadioButton('多文件')

        self.fileChoiceButtonGroup = QButtonGroup()
        self.fileChoiceButtonGroup.addButton(self.singleFile)
        self.fileChoiceButtonGroup.addButton(self.multipleFiles)

        self.singleFile.setChecked(True)
        '''

        self.selectFileButton = PrimaryPushButton("选择文件(支持多选")
        self.selectFileButton.clicked.connect(self.chooseFiles)

        #self.fileChoice.addWidget(self.singleFile)
        #self.fileChoice.addWidget(self.multipleFiles)
        #self.fileChoice.addWidget(self.selectFileButton)


        self.leftLayout.addWidget(self.selectFileButton)



        '''文件展示表格'''
        self.fileTable=TableWidget()
        self.fileTable.cellClicked.connect(self.showDetail)

        self.fileTable.setBorderVisible(True)
        self.fileTable.setBorderRadius(8)

        self.fileTable.setWordWrap(False)
        self.fileTable.setRowCount(0)
        self.fileTable.setColumnCount(5)

        fileInfos = []
        for i, fileInfos in enumerate(fileInfos):
            for j in range(5):
                self.fileTable.setItem(i, j, QTableWidgetItem(fileInfos[j]))

        self.fileSet = set()  #用于实现文件去重

        # 设置水平表头
        self.fileTable.setHorizontalHeaderLabels(['Name', 'Size', 'Type', 'State', 'Result'])
        self.leftLayout.addWidget(self.fileTable)

        self.startButton = PrimaryPushButton(FIF.ROBOT, '开始检查')
        self.startButton.clicked.connect(self.startAudit)
        self.leftLayout.addWidget(self.startButton)

        self.leftWidget = QWidget()
        self.leftWidget.setLayout(self.leftLayout)

        # ===== 右侧文本=====
        self.rightLayout = QVBoxLayout(self.leftWidget)
        self.resultText = PlainTextEdit()
        self.resultText.setPlainText("这里将会输出结果\nAI分析速度及准确性与所选用的模型有关")
        self.rightLayout.addWidget(self.resultText)

        self.rightWidget = QWidget()
        self.rightWidget.setLayout(self.rightLayout)

        self.mainLayout.addWidget(self.leftWidget, 1)
        self.mainLayout.addWidget(self.rightWidget, 1)

        self.leftWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.resultText.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        self.setStyleSheet("background: transparent;")

    def checkOptiLayout(self):
        self.use_static = self.staticAudit.isChecked()
        self.use_ai = self.aiAudit.isChecked()

        if self.use_static and self.use_ai:
            self.optiWidget.show()
        else:
            self.optiWidget.hide()



    #============一些消息条============
    #未填写api
    def AiTipFlyout(self):
        InfoBar.error(
            title='未填写API信息',
            content="填写API信息或禁用AI辅助语义分析功能",
            isClosable=False,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )
    #未选择文件
    def choicefileFlyout(self):
        InfoBar.error(
            title='未选择文件',
            content="请先选择至少一个文件",
            isClosable=False,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )

    # 未选择检查方式
    def choiceTypeFlyout(self):
        InfoBar.error(
            title='未选择检查方式',
            content="请至少选择一种检查方式",
            isClosable=False,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=3000,
            parent=self
        )
    #分析成功
    def successResultInfo(self):
        InfoBar.success(
            title='SUCCESS',
            content="分析完成！",
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,
            parent=self
        )

    #分析失败
    def errorResultInfo(self):
        InfoBar.error(
            title='ERROR',
            content="AI分析超时，仅输出静态分析结果\n请重试或检查api账户余额信息",
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=-1,
            parent=self
        )

    def chooseFiles(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文件",
            "",
            "All Files (*);;Python Files (*.py)"
        )
        if files:
            self.addFilesToTable(files)


    def addFilesToTable(self,files):
        for file in files:
            if not os.path.exists(file):
                    continue

            if file in self.fileSet:
                continue

            self.fileSet.add(file)
            row = self.fileTable.rowCount()
            self.fileTable.insertRow(row)

            # ===== 基础信息 =====
            fileName = os.path.basename(file)
            fileSize = os.path.getsize(file)
            fileType = os.path.splitext(file)[1].replace('.', '')

            # 转换大小（KB/MB）
            sizeStr = self.formatSize(fileSize)

            # ===== 填入表格 =====
            self.name=QTableWidgetItem(fileName)
            self.name.setData(Qt.ItemDataRole.UserRole, file) #把完整路径绑定避免重复文件名导致的错误去重
            self.fileTable.setItem(row, 0, self.name)

            self.fileTable.setItem(row, 1, QTableWidgetItem(sizeStr))
            self.fileTable.setItem(row, 2, QTableWidgetItem(fileType))

            # 初始状态
            self.fileTable.setItem(row, 3, QTableWidgetItem("待检查"))
            #这里攒一个设置颜色的命令
            #self.item = QTableWidgetItem("待检查")
            #self.item.setForeground(QColor("orange"))

            # 初始结果
            self.fileTable.setItem(row, 4, QTableWidgetItem("-"))

    def formatSize(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"

    #删除文件，目前没准备怎么实现但是先写着
    def removeFile(self, row):
        fileName = self.fileTable.item(row, 0).text()

        for f in list(self.fileSet):
            if os.path.basename(f) == fileName:
                self.fileSet.remove(f)

        self.fileTable.removeRow(row)

    def startAudit(self):
        if self.fileTable.rowCount() == 0:
            self.choicefileFlyout()
            return

        self.use_static = self.staticAudit.isChecked()
        self.use_ai = self.aiAudit.isChecked()
        self.use_assist=self.optiButton.isChecked()

        if not self.use_static and not self.use_ai:
            self.choiceTypeFlyout()
            return
        if self.use_ai:
            missing = self.check_ai_config()

            if missing:
                self.AiTipFlyout()
                return

        self.allResults = {}

        files = []

        for row in range(self.fileTable.rowCount()):

            item = self.fileTable.item(row, 0)

            if not item:
                continue

            file_path = item.data(Qt.ItemDataRole.UserRole)

            files.append((row, file_path))

            # 设置初始状态
            state_item = QTableWidgetItem("等待中")
            self.setItemColor(state_item, "等待中")
            self.fileTable.setItem(row, 3, state_item)

        self.worker =ScanThread(
            controller=self.controller,
            files=files,
            use_static=self.use_static,
            use_ai=self.use_ai,
            use_assist=self.use_assist
        )

        self.worker.progress.connect(self.updateScanStatus)
        self.worker.finished.connect(self.scanFinished)

        self.worker.start()

        self.auditResults = self.allResults
        # ===== 成功提示 =====
        self.successResultInfo()
        self.showSummaryPanel()

    def updateScanStatus(self, row, file_path,state_text, result_text, result_data):

        self.auditResults[file_path] = result_data

        state_item = QTableWidgetItem(state_text)
        self.setItemColor(state_item, state_text)
        self.fileTable.setItem(row, 3, state_item)

        result_item = QTableWidgetItem(result_text)
        self.setItemColor(result_item, result_text)
        self.fileTable.setItem(row, 4, result_item)

    def scanFinished(self, all_results):

        self.auditResults = all_results
        self.successResultInfo()
        self.showSummaryPanel()

    def summarize_results(self, results):
        summary = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0
        }

        for r in results:
            level = r.get("severity", "INFO").upper()
            if level in summary:
                summary[level] += 1

        return summary

    from PyQt6.QtGui import QColor

    def setItemColor(self, item, status):
        color_map = {
            # ===== 状态 =====
            "运行中": "orange",
            "完成": "green",
            "失败": "red",


            # ===== 审计结果 =====
            "安全": "green",
            "有风险": "orange",
            "错误": "red",
        }

        color = color_map.get(status)
        if color:
            item.setForeground(QColor(color))

    def updateTable(self):
        self.fileTable.setRowCount(len(self.auditResults))

        for row, (file, result) in enumerate(self.auditResults.items()):
            self.fileTable.setItem(row, 0, QTableWidgetItem(file))

            if result["total"] == 0:
                status = "无漏洞"

            else:
                status = "有漏洞"

            self.fileTable.setItem(row, 1, QTableWidgetItem(status))


    def updateRightPanel(self, file_path, result):
        issues = result.get("issues", []) or []
        status = result.get("status", "correct")
        static_count, ai_count = self.count_by_source(issues)
        total = max(static_count, ai_count)

        cursor = self.resultText.textCursor()
        self.resultText.clear()
        def insert(text, color=None, bold=False):
            fmt = QTextCharFormat()
            if color:
                fmt.setForeground(QColor(color))
            if bold:
                f = QFont()
                f.setBold(True)
                fmt.setFont(f)
            cursor.insertText(text, fmt)

        # ===== 标题 =====
        insert(f"文件：{os.path.basename(file_path)}\n")
        if status == "error":
            insert("状态：解析失败\n\n", color="red", bold=True)
            insert("=== 错误详情 ===\n\n", bold=True)
            return

        if self.use_ai and self.use_static and not self.use_assist:
            insert(f"漏洞总数：{total}  (STATIC:{static_count}, AI:{ai_count})\n\n", bold=True)
        else:
            insert(f"漏洞总数：{total}\n\n", bold=True)
        # ===== 无漏洞 =====
        if total == 0:
            insert("✅无漏洞\n")
            return
        # ===== 内容 =====
        insert("=== 漏洞详情 ===\n\n", bold=True)
        for i, issue in enumerate(issues, 1):
            source = issue.get("source", "unknown")
            if source == "ai":
                prefix = "[AI]"
            elif source == "static":
                prefix = "[STATIC]"
            else:
                prefix = "[UNK]"

            insert(f"[{i}] {prefix} {issue.get('name', 'Unknown')}\n")

            severity = issue.get('severity', 'INFO')

            if severity == "HIGH":
                color = "#ff4d4f"
            elif severity == "MEDIUM":
                color = "#faad14"
            elif severity == "LOW":
                color = "#1890ff"
            else:
                color = "black"

            insert("等级: ")
            insert(f"{severity}\n", color=color, bold=True)

            insert(f"行号: {issue.get('lineno', 0)}\n")
            insert(f"描述: {issue.get('message', '')}\n")

            insert("\n")

    def showDetail(self, row, column):
        file_item = self.fileTable.item(row, 0)
        if not file_item:
            return
        file_path = file_item.data(Qt.ItemDataRole.UserRole)
        result = self.auditResults.get(file_path)
        if not result:
            return
        self.updateRightPanel(file_path, result)

    def count_by_source(self, issues):
        static_count = 0
        ai_count = 0

        for i in issues:
            src = i.get("source", "")

            if "static" in src:
                static_count += 1
            if "ai" in src:
                ai_count += 1

        return static_count, ai_count

    def showSummaryPanel(self):
        text = "📌 点击左侧文件查看详细漏洞信息\n\n"

        for file_path, result in self.auditResults.items():
            file_name = os.path.basename(file_path)
            total = result["total"]
            issues = result["issues"]

            # ===== 统计不同等级 =====
            summary = {
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0
            }

            for issue in issues:
                level = issue.get("severity", "INFO").upper()
                if level in summary:
                    summary[level] += 1

            # ===== 拼接文本 =====
            text += f"文件：{file_name}\n"

            if total == 0:
                text += "检查结果：无漏洞\n"
                text += "漏洞总数：0\n\n"
            else:
                text += "检查结果：有漏洞\n"
                text += f"漏洞总数：{total} "
                text += f"(HIGH:{summary['HIGH']} "
                text += f"MEDIUM:{summary['MEDIUM']} "
                text += f"LOW:{summary['LOW']})\n\n"

        self.resultText.setPlainText(text)



    def check_ai_config(self):
        config = get_api_config()

        required_fields = ["api_key", "base_url", "model", "provider"]

        missing = [field for field in required_fields if not config.get(field)]

        return missing


class ScanThread(QThread):
    progress = pyqtSignal(int, str, str, str, object)
    finished = pyqtSignal(dict)

    def __init__(self,controller,files,use_static,use_ai,use_assist):
        super().__init__()
        self.controller = controller
        self.files = files

        self.use_static = use_static
        self.use_ai = use_ai
        self.use_assist = use_assist

    def run(self):

        all_results = {}

        for row, file_path in self.files:

            try:

                scan_result = self.controller.run_scan(
                    file_path,
                    use_static=self.use_static,
                    use_ai=self.use_ai,
                    use_assist=self.use_assist
                )

                results = scan_result.get("issues", []) or []
                status = scan_result["status"]

                all_results[file_path] = {
                    "status": status,
                    "total": len(results),
                    "issues": results
                }

                if status == "error":
                    result_text = "错误"
                    state_text = "失败"

                elif len(results) == 0:
                    result_text = "安全"
                    state_text = "完成"

                else:
                    result_text = "有风险"
                    state_text = "完成"

                self.progress.emit(row,file_path,state_text,result_text,all_results[file_path])

            except Exception as e:

                self.progress.emit(
                    row,
                    "失败",
                    "UI ERROR",
                    {}
                )

        self.finished.emit(all_results)