#!/usr/bin/env python
# -*- coding: utf-8 -*-

from downloader import Main
import apscheduler.scheduler as ApSched
import random

# Check updates two times in a day(random time).
r_hours = random.randint(8, 11)
r_minutes = random.randint(0, 59)
sched = ApSched.Scheduler(standalone=True, coalesce=True)
sched.add_interval_job(Main.main, hours=r_hours, minutes=r_minutes)

# Check updates two times in a day(fixed time)
# sched.add_cron_job(Main.main, hour=21)
# sched.add_cron_job(Main.main, hour=7)

sched.start()
