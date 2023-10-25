import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

html = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>        
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    </head>
    <body> <h2 id="header">Header.</h2> </body>
    <script>
        var backend;
        new QWebChannel(qt.webChannelTransport, function (channel) {
            backend = channel.objects.backend;
        });

        document.getElementById("header").addEventListener("click", function(){
            backend.foo();
        });
    </script>
</html>
'''

class HelloWorldHtmlApp(QWebEngineView):

    def __init__(self):
        super().__init__()

        # setup a page with my html
        my_page = CustomWebEnginePage(self)
        my_page.setHtml(html)
        self.setPage(my_page)

        # setup channel
        self.channel = QWebChannel()
        self.channel.registerObject('backend', self)
        self.page().setWebChannel(self.channel)
        self.show()

    @pyqtSlot()
    def foo(self):
        print('bar')

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # Override the JavaScriptConsoleMessage method
        print(f"JavaScript Console Message: Level {level}, Message: {message}, Line Number: {lineNumber}, Source ID: {sourceID}")


if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    view = HelloWorldHtmlApp()
    view.show()
    app.exec_()