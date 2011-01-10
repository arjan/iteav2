# Copyright (c) 2011 Arjan Scherpenisse
# See LICENSE for details.

import time
import clutter
import cairo
import math
import random

from twisted.internet import task

from sparked.graphics import stage


class Stage(stage.Stage):

    def created(self):
        #clutter.set_default_frame_rate(10)
        self.set_color(clutter.color_from_string("Black"))
        self.bs = {}
        def spawn():
            self.addLine(random.choice(self.app.lines))
        task.LoopingCall(spawn).start(5)

    def addLine(self, line):
        ts = time.time()
        txt = CircularText(line, "Georgia", 30, False)
        self.add(txt)
        txt.set_position(800, 600)

        start = random.random() * 360
        b1 = BehaviourTextRotate(1, 400, start, start+360, 20)
        b1.apply(txt)

        def makeRm(t):
            def rm():
                del self.bs[t]
            return rm
        b2 = BehaviourFadeAndDestroy(20, makeRm(ts))
        b2.apply(txt)
        self.bs[ts] = (b1, b2)



        
class BehaviourTextRotate(clutter.Behaviour):
    __gtype_name__ = 'BehaviourTextRotate'

    def __init__(self, initialRadius, finalRadius, initialAngle, finalAngle, time):
        clutter.Behaviour.__init__(self)

        self.time = time
        self.initialAngle = initialAngle
        self.finalAngle = finalAngle
        self.initialRadius = initialRadius
        self.finalRadius = finalRadius

        self.timeline = clutter.Timeline(1000 * time)
        alpha = clutter.Alpha(self.timeline, clutter.EASE_OUT_CUBIC)
        self.set_alpha(alpha)
        self.timeline.connect("completed", self.setLooping)
        self.timeline.start()
        self.looping = False

    def setLooping(self, t):
        t = (self.finalAngle - self.initialAngle) / 360.0 * self.time
        self.timeline = clutter.Timeline(int(t * 1000))
        alpha = clutter.Alpha(self.timeline, clutter.LINEAR)
        self.set_alpha(alpha)
        self.timeline.start()
        self.timeline.set_loop(True)
        self.looping = True


    def do_alpha_notify(self, alpha_value):
        if not self.looping:
            r = self.initialRadius + alpha_value * (self.finalRadius-self.initialRadius)
            a = self.initialAngle + self.timeline.get_progress() * (self.finalAngle - self.initialAngle)
        else:
            r = self.finalRadius
            a = self.finalAngle + self.timeline.get_progress() * 360

        for actor in self.get_actors():
            actor.set_radius(r, a)


class BehaviourFadeAndDestroy(clutter.Behaviour):
    __gtype_name__ = 'BehaviourFadeAndDestroy'

    def __init__(self, time, callback):
        clutter.Behaviour.__init__(self)
        self.time = time
        timeline = clutter.Timeline(1000 * time)
        alpha = clutter.Alpha(timeline, clutter.EASE_IN_EXPO)
        self.set_alpha(alpha)
        def bye(t):
            for a in self.get_actors(): a.destroy()
            callback()
        timeline.connect("completed", bye)
        timeline.start()

    def do_alpha_notify(self, alpha_value):
        for actor in self.get_actors():
            actor.set_opacity(255 - alpha_value*255)



class CircularText(clutter.Group):

    def __init__(self, txt, font="Georgia", fontsize=40, inside=True):
        clutter.Group.__init__(self)
        self.text = txt
        self.hide()
        self.fontsize = fontsize
        self.font = font
        self.inside = inside

        self.w = 2 * fontsize
        self.w2 = self.w/2
        self.actors = []

        x = 0
        y = 0
        for letter in self.text:
            t = clutter.CairoTexture(self.w, self.w)
            t.set_anchor_point(self.w2, self.w2)
            t.set_position(x, y)
            self.add(t)

            cr = t.cairo_create()
            # cr.move_to(self.w2,  self.w2)
            # cr.set_source_rgb(1.0, 0.0, 0.0)
            # cr.arc(self.w/2, self.w/2, 3, 0, 6.28)
            # cr.fill()

            cr.move_to(self.w2,  self.w2)

            cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.select_font_face(self.font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(self.fontsize)
            self.fheight = cr.font_extents()[2]

            cr.show_text(letter)
            xb, yb, width, height, xa, ya = cr.text_extents(letter)

            self.actors.append({'texture': t, 'letter': letter, 'offset': x, 'width': width})
            x += xa

        self.totalx = float(x)


    def set_radius(self, radius, alpha):
        start_alpha = alpha / (180.0/math.pi)

        if not self.inside:
            radius += self.fheight

        o = radius * 2 * math.pi
        b = 2*math.pi*(self.totalx/o)

        if not self.inside:
            b = -b

        oy = 0
        d = 0
        for act in self.actors:
            tex = act['texture']
            d += act['offset']

            f = (act['offset']) / self.totalx
            alpha = start_alpha + b * f

            oy = radius * math.sin(alpha)
            ox = radius * math.cos(alpha)

            f = (act['offset']+act['width']*.5) / self.totalx
            alpha = start_alpha + b * f

            angle = alpha*(180.0/math.pi)+90
            if not self.inside:
                angle += 180
            tex.set_rotation(clutter.Z_AXIS, angle, 0, 0, 0)
            tex.set_position(ox,oy)
        self.show_all()


