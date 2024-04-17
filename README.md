# Techlahoma Data Tool

A project made at Atlas School to benefit Techlahoma and the great work it does for the tech scene in Oklahoma.

This repository represents the code *as it appeared on Demo Day*, after 2 weeks of planning and actual development time.

## Introduction

For our final project at Atlas School, we were very excited to create a tool that would serve a real need at an Oklahoma nonprofit so many of our peers and instructors already know and love -- Techlahoma.

Techlahoma's mission is to enrich Oklahoma's technologists of all backgrounds through education, connection, and opportunity. They've got thousands of members. They host conferences, they run a coding bootcamp, and they support 18 different volunteer-run user-groups.

... and that's just scratching the surface!

They do so much good for the tech scene in Oklahoma, and we wanted to do something good for them. So we approached them to learn more about their technological needs and learned that as their organization grows, so does the need to quantify their impact. If we could help them build up good data on who they were serving with their programs, it could really help in the grant application process. And that could help them have an even bigger impact in the future!

We wanted to help them get good data about who was attending their volunteer-run technology meet-ups and user groups. And we wanted do it in a way that didn't put any extra work on the plates of the volunteers. They already do so much!

So we set about to design a tool that would incentivize their constituents to check in to events and optionally share more information about themselves. We wanted it to be easy, fun, and rewarding — and most importantly, we wanted it to work with the existing systems Techlahoma already used for reporting.

## The Product Idea

[image] Flowchart [/image]

The basic idea of the project was simple:
- Constituents would be prompted, in the course of the normal pre-meeting announcements/slides, to scan a QR code or go to an easy-to-remember URL.
- From there, they would be able to log in to our webapp using their pre-existing Techlahoma account. This authentication would allow us to link the constituent to their member record in Techlahoma's CRM database.
- Once logged in, the user would be able to check in for the event and earn points for this action.
- Points would be tracked and
- If appropriate, the user would be able to optionally share additional information about themselves, making it easier to connect them with future Techlahoma events and offerings. Some of this optional information, like zip codes, could addtionally be really helpful in preparing grant applications.
- All information, like check-in events and optional data updates, would be synced with the constituent's internal profile in Techlahoma's CRM system.

## Tools Used

Because Techlahoma already has a data stack, we had to build something that would integrate with that.

We wrote code to use their Neon CRM database, building out authentication and API queries to identify users and store interaction data… as well as information about the incentives program.

Because we wanted staff to be able to change points and rewards without coding, we made forms on their CRM admin panel that could update underlying data.

We also really wanted it to look and feel like Techlahoma's brand. We used tools like Canva and Figma for designing and prototyping.

Our code base was almost entirely Python. We used Flask to build our server and kept our code secure by using Redis for server-side session management.
And we deployed it in the cloud so people could access it.

## App Demo

[image]app demo phone recording[/image]


