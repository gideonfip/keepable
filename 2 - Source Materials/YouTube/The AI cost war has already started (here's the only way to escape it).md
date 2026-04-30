---
title: "The AI cost war has already started (here's the only way to escape it)"
source: "https://www.youtube.com/watch?v=wJsJSrbYeds"
author:
  - "[[Gideon Ng Builds]]"
published: 2026-04-30
created: 2026-04-30
description: "Escape the AI cost war by building effective Skills. The only way to prevent yourself from being locked in with one provider."
tags:
  - defuddle
favourites: false
---

## Transcript

**0:00** — If you're an AI user, you're currently stuck in this AI cost war. This has been happening for quite a while, but over the past few months, it has just gotten worse as more people start to use AI and all of these providers can't keep up with the demand. Today, I'll be showing you the only way that you can escape this war.

The cost of running AI is getting worse and worse. Just recently, our co-pilot paused all of their pro plans with research limits getting tighter. I previously shared my thoughts on the price increase for size coding plans where they did this without any announcements at all.

**0:30** — This is a trend that will happen across all of the different model providers and aggregators as the cost of influence just keeps getting higher. The new models that are being released by all of these frontier companies seem to get worse as well.

**0:49** — And I've seen many complaints about how it's worse, how others have switched back to Sonnet, and I just feel it's because all of these companies are rushing out updates to make it seem like they're constantly innovating, constantly pushing out new and cool stuff, and to also keep the pace of all of the open-source models, like recently the Kimi K2.6 as well as GLM 5.1.

**1:12** — In this entire mad rush to push out as many updates as they can, the models become extremely underwhelming. And right now, everyone is becoming more worried about what this cost war means to their entire AI system. All of the influence that we are running right now is heavily subsidized. And it's very possible that eventually most of us who are on these cheaper plans either get priced out by the huge price increases or we still get to use these plans, but with incredibly aggressive rate limits.

**1:39** — Some people have already experienced hitting the rate limits with just a few requests, and I'm quite sure that this will be the norm in the future, especially for all of the different cheap plans. In this current situation, we need to have that flexibility to hop between models, switch between them, and still be able to get similar results.

**1:57** — The best models that you're using right now may not be the best in a few weeks' time or even tomorrow when another provider drops a new update. And the moment you get locked in with one of these providers, you're essentially stuck and subject to them changing their terms at any time. And that's why I designed my entire AI system with portability in mind. It is not an agentic system that runs by itself, but I'm using it to automate most of the tasks in my daily life.

**2:21** — I want that flexibility and the portability where I can easily switch between any models that I want without being locked in and without losing control of my data. I designed my portable AI system around these eight key components. You could check some of my previous videos that mention about this, but today I'll be focusing on the one that I believe is the most important, which is skills.

**2:44** — So, one of the important framings that you want to have is that the models are just your employees, you're a manager, and you need to give these models clear SOPs on how they execute tasks that you want them to. This was a Reddit post that I saw in Singapore, which complains about how confused and lost an intern was when the manager asked the intern to execute certain tasks and they took it too literally.

**3:12** — This is a very good example of what happens when you don't have a clear SOP, you don't give your employees, your interns, or even your models clear instructions on how you exactly want to execute this task. And on the right there's something that I've heard Ali Abdaal talk a lot about where he gives McDonald's as an example of how well-executed the entire branch is.

**3:35** — You'll more or less get the same experience by eating at two completely different branches across the entire world. And the reason why that is possible is because of a highly systematized way of running the entire branch. Building out all of these systems are very important in the way that you work with AI because once you give it clear instructions, the model knows what to execute.

**3:55** — If you take the time to build out these skills or SOPs or instructions, depending on how you want to call them, they can be invoked at any time and you can get the same exact output even when you're switching between models because your instructions and your skills are clear enough so that any model can read it, understand, and execute it in the way that you want.

**4:20** — Some of them I created for myself, some have been adapted from what I see online, and I'm able to execute any of them by just typing out a slash command. The only way that you can escape the AI cost war is to prevent yourself from being locked in with one provider. You need to build good skills so that you can switch your models easily. And today I'll be sharing with you this signal framework that I've developed on how you can build these good skills.

**4:51** — The SIGNAL framework is an acronym for six different steps. Let me guide you through how I would build out a new skill based on the skill that I just created using this framework. This skill was meant to track all of my different expenses that I have for my business.

**5:15** — I didn't want to manually enter all of the details, so I decided to create a skill. And the very first step of this SIGNAL framework is **Spotting the bottleneck**. Let's take a look at all of your different workflows and try to identify the bottleneck. What is one soul-sucking, repetitive task that you hate doing that's preventing you from completing the entire workflow?

**5:45** — Similar to the McDonald's example, you can think of every workflow as a system, and it requires a lot of steps to execute and give you the output that you want.

**6:10** — The more context that you give to the AI, the easier it is to understand your workflow and how it should be executing it based on your preferences, and it can suggest a tailored solution that works for that specific workflow.

**6:39** — After you share everything with the AI, the next part is **Integrating the step**. Your skills can be extremely simple where it's just one SOP within the skill markdown file, or it could include prompts, it could include scripts, or even instructions on how to execute different scenarios. And that's why I believe that skills are so much better than just simple prompts.

**7:01** — The more detailed description that you give to AI, including all of the different tools that you use, the easier it is for the model to recommend to you what are the exact tools that you require.

**7:28** — Now that the AI has a better understanding of the entire process, the next step is to **Guide the LLM** while you're running through the entire process with them. This is definitely the most tedious part because you have to go through with the LLM exactly how you want it to be executed.

**8:18** — It will definitely not be perfect the very first time, and you need to guide the LLM, tell it where it went wrong, what are the different steps, what is it that you actually wanted, and just keep prompting it to build up this skill.

**8:46** — The ultimate goal of this is to get the **gold standard** of the entire workflow. What this means is that you have a desired output that you want the workflow to run and execute it to give you that desired output. And once you actually get that, that means you've hit the gold standard and it now can be implemented as a skill.

**9:15** — Spending that time right now is so crucial so that you don't need to tell the LLM in the future that this is not the output that you want.

**9:41** — Once you finally get that gold standard, you invoke the **skill creator skill**. This is the one by Anthropic, and basically you don't need to write anything, you don't need to know any of the code. If the AI decides to write the script or even create a prompt to execute the task, all of these will be automatically added into the skill.

**10:48** — So I've shared quite a bit about building out these skills and let me just quickly show you how it's actually like in action. Right now, I'm inside of my signal OS. This is my file system that basically runs through all of the different aspects of my life.

**11:04** — All of the skills that you create are found inside your `.agents` or `.clock` file depending on which CLI or platform that you're using. The reason why I'm using inside of the `.agents` file is because I switched over to open code from Claude and I chose to do that because it's so easy to switch between all of the different model providers.

**11:51** — I have roughly about 105 skills. Of course, this is not ideal because it can be quite bloated. Some of them I've barely used in quite a while. The way that I've named them is based on the domain.

**12:36** — Again, you don't need to worry about how to write this entire skill because if you use the skill creator skill, everything is done for you. You can see some things like, let's say Typefully next slot. This is the one that actually helps me to identify what is the next best slot for me to schedule out a tweet. And in this case, there are different configurations apart from just the skill.md. The AI created a script that helps to schedule the next slot where it uses the Typefully API.

**13:08** — I just gave the AI my Typefully API key and I told them that I wanted to execute this. So long as it's something that's repeatable that you constantly want to execute, you can just turn it into a skill so that all you need to do is just type out a slash command and you can execute the skill right away.

**13:38** — I'll be showing you that inside of my system. I'm using open code inside of Warp. I shared more about why I decided to use this setup in my previous video which I'll link in the description. And once you're inside of open code, you can then choose to invoke any of the skills by just typing slash skills.

**14:19** — These are all the skills I can invoke at any time. So in this case, I can do something like learnings YouTube. Basically, what it does is it fetches a transcript from one of the YouTube videos and then it generates a summary for me.

**14:48** — I'll be sharing with you the SIGNAL skill framework so that you can just invoke it inside of open code. What I just need to do here is to search for the skill SIGNAL framework and then I can launch it. In this case, I'm using the Gemma 4 31B inside of Google AI Studio and it's very generous with about 1.5K free requests per day.

**15:16** — Another important skill that you need to have inside is called the skill creator. This is actually not what I created but it's inside of Anthropic's GitHub which I then modified to use it for my open code configuration because what the skill.md does is that it will add the skill inside of the .clock folder. So I want to specify that I actually want to add it inside the .agents folder so that I can invoke it inside of open code.

**16:21** — You can also see that it takes quite a while for Gemma 4 to come up with a response and the main reason why is because it's free. You can see that there's this internal error being encountered as well. So I wouldn't really expect too much when I'm using all these free models because a lot of limitations as compared to using the paid versions of it.

**16:55** — Skills are just one part of my entire portable AI system. There are seven other components that are required to ensure that everything is running well where you can build your skills and your system once and you can easily switch at any time to any model that you want.
