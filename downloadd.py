#!/usr/bin/env python
# -*- coding: utf-8 -*-

from downloader import Main
import apscheduler.scheduler as ApSched

sched = ApSched.Scheduler(standalone=True, coalesce=True)
sched.add_cron_job(Main.main, hour=21)
sched.add_cron_job(Main.main, hour=7)
sched.start()
