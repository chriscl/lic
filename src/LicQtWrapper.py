"""
    Lic - Instruction Book Creation software
    Copyright (C) 2010 Remi Gagne

    This file (LicQtWrapper.py) is part of Lic.

    Lic is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Lic is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/
"""

from LicCommonImports import *

NoFlags = QGraphicsItem.GraphicsItemFlags()
NoMoveFlags = QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable
AllFlags = NoMoveFlags | QGraphicsItem.ItemIsMovable

__all__ = ["NoFlags", "NoMoveFlags", "AllFlags",
           "GraphicsRoundRectItem", "GraphicsCircleLabelItem",
           "GraphicsRotateArrowItem"]

def genericNormalizePosition(self, childrenToSkip = []):
    x, y = self.rect().topLeft()
    if x == 0 and y == 0:
        return
    self.moveBy(x, y)
    for item in self.childItems():
        if item not in childrenToSkip:
            item.moveBy(-x, -y)
    self.setRect(0, 0, self.rect().width(), self.rect().height())

QGraphicsRectItem.normalizePosition = genericNormalizePosition

def genericLineNormalizePosition(self):
    x, y = self.line().p1()
    if x == 0 and y == 0:
        return
    self.moveBy(x, y)
    self.setLine(0, 0, self.line().x2() - x, self.line().y2() - y)

QGraphicsLineItem.normalizePosition = genericLineNormalizePosition

def genericSetPosCenteredIn(self, rect):
    x = (rect.width() - self.rect().width()) / 2.0
    y = (rect.height() - self.rect().height()) / 2.0
    self.setPos(x, y)

QGraphicsRectItem.setPosCenteredIn = genericSetPosCenteredIn
QGraphicsSimpleTextItem.setPosCenteredIn = genericSetPosCenteredIn

def genericGetOrientedSize(self, orientation):
    return self.width() if orientation == LicLayout.Horizontal else self.height()

QRectF.getOrientedSize = genericGetOrientedSize

def genericDrawSelectionRect(self, rect, cornerRadius = 0):
    self.save()
    pen = QPen(Qt.DashLine)
    pen.setWidth(2)
    self.setPen(pen)
    self.setBrush(Qt.NoBrush)
    if cornerRadius:
        self.drawRoundedRect(rect, cornerRadius, cornerRadius)
    else:
        self.drawRect(rect)
    self.restore()

QPainter.drawSelectionRect = genericDrawSelectionRect

class GraphicsRoundRectItem(QGraphicsRectItem):
    
    def __init__(self, parent):
        QGraphicsRectItem.__init__(self, parent)
        
    def paint(self, painter, option, widget = None):

        settings = self.getClassSettings()
        painter.setPen(settings.pen)
        painter.setBrush(settings.brush)

        if settings.pen.cornerRadius:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawRoundedRect(self.rect(), settings.pen.cornerRadius, settings.pen.cornerRadius)
        else:
            painter.drawRect(self.rect())

        if self.isSelected():
            painter.drawSelectionRect(self.rect(), settings.pen.cornerRadius)
    
    def pen(self):
        return self.getClassSettings().pen
    
    def setPen(self, newPen):
        settings = self.getClassSettings()
        settings.pen = newPen

    def brush(self):
        return self.getClassSettings().brush
        
    def setBrush(self, newBrush):
        settings = self.getClassSettings()
        settings.brush = newBrush
    
class GraphicsCircleLabelItem(QGraphicsEllipseItem):

    itemClassName = "GraphicsCircleLabelItem"
    defaultPen = QPen(Qt.black)
    defaultBrush = QBrush(Qt.white)
    defaultFont = QFont("Arial", 8)
    defaultDiameter = 18

    def __init__(self, parent, length = "10"):
        QGraphicsEllipseItem.__init__(self, 0, 0, self.defaultDiameter, self.defaultDiameter, parent)
        self.setPen(self.defaultPen)
        self.setBrush(self.defaultBrush)

        self._row = 1
        self.setFont(self.defaultFont)
        self.lengthText = length
        self.labelColor = QColor(Qt.black)  # TODO: implement Part length label color
        self.data = lambda index: "Length Indicator (%s)" % length

    def paint(self, painter, option, widget = None):
        QGraphicsEllipseItem.paint(self, painter, option, widget)
        painter.setPen(QPen(self.labelColor))
        painter.setFont(self.font())
        textRect = painter.boundingRect(self.rect(), Qt.AlignCenter, self.lengthText)
        painter.drawText(textRect, Qt.AlignCenter, self.lengthText)

    def setDiameter(self, diameter):
        self.setRect(0, 0, diameter, diameter)

    def diameter(self):
        return self.rect().width()

    def setFont(self, font):
        self._font = font
        
    def font(self):
        return self._font

class GraphicsRotateArrowItem(GraphicsRoundRectItem):

    itemClassName = "GraphicsRotateArrowItem"
    arrowTipLength = 9.0
    arrowTipHeight = 4.0
    ArrowHead = QPolygonF([QPointF(),
                           QPointF(arrowTipLength + 2.5, -arrowTipHeight),
                           QPointF(arrowTipLength, 0.0),
                           QPointF(arrowTipLength + 2.5, arrowTipHeight)])

    def __init__(self, parent):
        GraphicsRoundRectItem.__init__(self, parent)
        self.data = lambda index: "Rotation Icon"
        self.setRect(0, 0, 50, 50)

    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.Antialiasing)
        GraphicsRoundRectItem.paint(self, painter, option, widget)
        painter.setPen(self.getClassSettings().arrowPen)
        painter.setBrush(QBrush(Qt.transparent))
        
        w, h2 = self.rect().width(), self.rect().height() / 2.0
        inset = 6.0
                
        start = QPointF(inset, h2 - inset)
        end = QPointF(w - inset, h2 - inset)
        
        ix, iy = inset * 1.8, inset * 2.5  # 1.8 & 2.5 entirely qualitative, for a 'nice' curve
        path = QPainterPath()
        path.moveTo(start)
        path.cubicTo(start + QPointF(ix, -iy), end + QPointF(-ix, -iy), end)

        start += QPointF(0, inset + inset)
        end += QPointF(0, inset + inset)
        path.moveTo(end)
        path.cubicTo(end + QPointF(-ix, iy), start + QPointF(ix, iy), start)

        painter.drawPath(path)

        painter.setBrush(QBrush(self.getClassSettings().arrowPen.color()))
        painter.save()
        painter.translate(w - inset, h2 - inset)
        painter.rotate(-135)
        painter.drawPolygon(GraphicsRotateArrowItem.ArrowHead)
        painter.restore()

        painter.save()
        painter.translate(inset, h2 + inset)
        painter.rotate(45)
        painter.drawPolygon(GraphicsRotateArrowItem.ArrowHead)
        painter.restore()

# Make QPoint iterable: p[0] is p.x, p[1] is p.y.  Useful for easily unpacking x & y.
def pointIterator(self, index):
    if index == 0:
        return self.x()
    if index == 1:
        return self.y()
    raise IndexError
QPoint.__getitem__ = pointIterator
QPointF.__getitem__ = pointIterator

# Make QSize iterable: p[0] is width, p[1] is height.  Useful for easy unpacking.
def sizeIterator(self, index):
    if index == 0:
        return self.width()
    if index == 1:
        return self.height()
    raise IndexError
QSize.__getitem__ = sizeIterator
QSizeF.__getitem__ = sizeIterator

# Make QRect iterable: p[0] is x, p[1] is y, p[2] is width, p[3] is height.  Useful for easy unpacking.
def rectIterator(self, index):
    if index == 0:
        return self.x()
    if index == 1:
        return self.y()
    if index == 2:
        return self.width()
    if index == 3:
        return self.height()
    raise IndexError
QRect.__getitem__ = rectIterator
QRectF.__getitem__ = rectIterator

def betterToString(self):
    return super.__str__(self).replace(self.__module__, "")[1:]
QPointF.__str__ = betterToString
QRectF.__str__ = betterToString

def genericGetSceneCorners(self):
    topLeft = self.mapToScene(self.mapFromParent(self.pos())) # pos is in item.parent coordinates
    bottomRight = topLeft + QPointF(self.boundingRect().width(), self.boundingRect().height())
    return topLeft, bottomRight

def genericGetSceneCornerList(self):
    tl, br = self.getSceneCorners()
    return [tl.x(), tl.y(), br.x(), br.y()]

def genericGetOrderedCornerList(self, margin = None):
    r, pos = self.rect(), self.pos()
    if margin:
        r.adjust(-margin.x(), -margin.y(), margin.x(), margin.y())
    return [r.topLeft() + pos, r.topRight() + pos, r.bottomRight() + pos, r.bottomLeft() + pos]

def genericRect(self):
    return self.boundingRect()

QGraphicsSimpleTextItem.rect = genericRect
QGraphicsPixmapItem.rect = genericRect

# This is necessary because Qt distinguishes between QContextMenuEvent and 
# QGraphicsSceneContextMenuEvent.  I guess its a C++ thing.  bleh
# Python is perfectly happy simply accepting event.  Be sure to convert the appropriate event
# parameters when passing one where another is expected though (like TreeView.contextMenuEvent)
QGraphicsItem.contextMenuEvent = lambda self, event: event.ignore()

QGraphicsItem.getPage = lambda self: self.parentItem().getPage()
QGraphicsItem.getInstructions = lambda self: self.getPage().instructions
QGraphicsItem.getAllSettings = lambda self: self.getInstructions().templateSettings
QGraphicsItem.getClassSettings = lambda self: self.getAllSettings().__getattribute__(self.itemClassName)
QGraphicsItem.getContext = lambda self: self.getInstructions().glContext
QGraphicsItem.getSceneCorners = genericGetSceneCorners
QGraphicsItem.getSceneCornerList = genericGetSceneCornerList
QGraphicsItem.getOrderedCorners = genericGetOrderedCornerList

def genericMousePressEvent(className):
    def _tmp(self, event):
        if event.button() == Qt.RightButton:
            return
        className.mousePressEvent(self, event)
        for item in self.scene().selectedItems():
            item.oldPos = item.pos()

    return _tmp

def genericMouseMoveEvent(className):
    
    def _tmp(self, event):
        if event.buttons() == Qt.RightButton or self.oldPos is None:
            return
        className.mouseMoveEvent(self, event)
        if self.parentItem() and (self.flags() & QGraphicsItem.ItemIsMovable) == QGraphicsItem.ItemIsMovable:
            self.scene().snap(self)
        #snapToGrid(self)
    return _tmp
    
def genericMouseReleaseEvent(className):
    
    def _tmp(self, event):
        if event.button() == Qt.RightButton:
            return
        scene = self.scene()
        className.mouseReleaseEvent(self, event)
        if self.oldPos is not None and self.pos() != self.oldPos:
            scene.emit(SIGNAL("itemsMoved"), scene.selectedItems())
        self.oldPos = None
        scene.xSnapLine.hide()
        scene.ySnapLine.hide()

    return _tmp

QGraphicsItem.oldPos = None  # Give all items an oldPos; saves a hasAttr check in mouseRelease
QGraphicsItem.fixedSize = False # Give all items an unset FixedSize 

QGraphicsLineItem.mousePressEvent = genericMousePressEvent(QGraphicsItem)
QGraphicsLineItem.mouseMoveEvent = genericMouseMoveEvent(QGraphicsItem)
QGraphicsLineItem.mouseReleaseEvent = genericMouseReleaseEvent(QGraphicsItem)

QGraphicsRectItem.mousePressEvent = genericMousePressEvent(QAbstractGraphicsShapeItem)
QGraphicsRectItem.mouseMoveEvent = genericMouseMoveEvent(QAbstractGraphicsShapeItem)
QGraphicsRectItem.mouseReleaseEvent = genericMouseReleaseEvent(QAbstractGraphicsShapeItem)

QGraphicsEllipseItem.mousePressEvent = genericMousePressEvent(QAbstractGraphicsShapeItem)
QGraphicsEllipseItem.mouseMoveEvent = genericMouseMoveEvent(QAbstractGraphicsShapeItem)
QGraphicsEllipseItem.mouseReleaseEvent = genericMouseReleaseEvent(QAbstractGraphicsShapeItem)

QGraphicsSimpleTextItem.mousePressEvent = genericMousePressEvent(QAbstractGraphicsShapeItem)
QGraphicsSimpleTextItem.mouseMoveEvent = genericMouseMoveEvent(QAbstractGraphicsShapeItem)
QGraphicsSimpleTextItem.mouseReleaseEvent = genericMouseReleaseEvent(QAbstractGraphicsShapeItem)

QGraphicsPixmapItem.mousePressEvent = genericMousePressEvent(QGraphicsItem)
QGraphicsPixmapItem.mouseMoveEvent = genericMouseMoveEvent(QGraphicsItem)
QGraphicsPixmapItem.mouseReleaseEvent = genericMouseReleaseEvent(QGraphicsItem)

def getFilename(self):
    if not self.hasFormat("text/uri-list"):
        return None
    filename = str(self.data("text/uri-list"))
    if len(filename) < 10 or filename[:8] != 'file:///':
        return None
    return filename[8:].strip() # trim off leading 'file:///' from uri

QMimeData.getFilename = getFilename
