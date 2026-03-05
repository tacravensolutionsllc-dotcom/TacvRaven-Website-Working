#!/usr/bin/env python3
"""
Black Wing Dispatch - Content Generators
TacRaven Solutions LLC

Generates long-form, paragraph-focused blog content in plain language.
Target: 2,300-3,000 words per post.
Includes anti-repetition protection for topics and content blocks.
"""

import random
import hashlib
import json
import os
from datetime import datetime

# State file for tracking used content
CONTENT_STATE_FILE = "content_state.json"


def load_content_state():
    """Load content generation state."""
    if os.path.exists(CONTENT_STATE_FILE):
        with open(CONTENT_STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "used_topics": [],
        "used_intro_indices": {},
        "used_background_indices": {},
        "used_technical_indices": {},
        "topic_cooldown": {},
        "last_categories": [],
    }


def save_content_state(state):
    """Save content generation state."""
    with open(CONTENT_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_topic_available(topic, state, cooldown_days=30):
    """Check if a topic can be used (not recently covered)."""
    topic_key = topic.lower().strip()
    
    if topic_key in state.get("topic_cooldown", {}):
        last_used = datetime.fromisoformat(state["topic_cooldown"][topic_key])
        days_since = (datetime.now() - last_used).days
        if days_since < cooldown_days:
            return False
    return True


def mark_topic_used(topic, state):
    """Mark a topic as recently used."""
    topic_key = topic.lower().strip()
    if "topic_cooldown" not in state:
        state["topic_cooldown"] = {}
    state["topic_cooldown"][topic_key] = datetime.now().isoformat()
    
    if "used_topics" not in state:
        state["used_topics"] = []
    state["used_topics"].append(topic_key)
    state["used_topics"] = state["used_topics"][-100:]


def check_category_rotation(category, state):
    """Ensure we don't repeat the same category too often."""
    last_cats = state.get("last_categories", [])
    if category in last_cats[-2:]:
        return False
    return True


def mark_category_used(category, state):
    """Track category usage for rotation."""
    if "last_categories" not in state:
        state["last_categories"] = []
    state["last_categories"].append(category)
    state["last_categories"] = state["last_categories"][-8:]


def select_from_pool(pool, category, pool_name, state):
    """Select from a pool avoiding recently used indices."""
    key = f"used_{pool_name}_indices"
    if key not in state:
        state[key] = {}
    if category not in state[key]:
        state[key][category] = []
    
    used = state[key][category]
    available = [i for i in range(len(pool)) if i not in used]
    
    if not available:
        state[key][category] = []
        available = list(range(len(pool)))
    
    idx = random.choice(available)
    state[key][category].append(idx)
    state[key][category] = state[key][category][-max(2, len(pool) // 2):]
    
    return pool[idx]


# =============================================================================
# INTRODUCTION PARAGRAPHS - Plain language, conversational (~300-400 words each)
# =============================================================================

INTRO_PARAGRAPHS = {
    "APT Activity": [
        """If you work in cybersecurity, you have probably heard the term APT thrown around a lot. Advanced Persistent Threat. It sounds intimidating, and honestly, it should be. These are not your everyday hackers looking for a quick score. These are organized groups, often backed by nation-states, with specific goals and the patience to achieve them over months or even years.

I have been tracking APT activity for a while now, and what strikes me most is how methodical these groups are. They do not rush. They research their targets, find the right entry points, and move carefully through networks without triggering alarms. By the time most organizations realize something is wrong, the attackers have already achieved their objectives.

This post digs into what we are seeing with APT activity right now. I will explain how these operations work, what makes them different from ordinary cybercrime, and what you can realistically do to protect your organization. The threat is serious, but understanding it is the first step toward defending against it.""",

        """Nation-state hacking sounds like something out of a spy movie, but it is very real and affecting organizations right now. Governments around the world have cyber units dedicated to intelligence gathering, intellectual property theft, and in some cases, preparing for potential conflicts by positioning themselves inside critical systems.

The challenge for defenders is that these groups have resources and time that most criminal hackers do not. They can develop custom tools, exploit zero-day vulnerabilities, and maintain access to compromised networks for extended periods. When you are up against an adversary with essentially unlimited resources and patience, traditional security approaches often fall short.

In this post, I want to share what we know about current APT operations based on public reporting and government advisories. More importantly, I want to talk about what this means for organizations trying to protect themselves. The situation is serious, but there are practical steps you can take to make yourself a harder target.""",

        """Every week seems to bring new reports about state-sponsored hacking campaigns. Government agencies issue advisories, security companies publish research, and the news covers the latest breach. But what does all this actually mean for someone trying to defend their network?

I want to cut through some of the noise and talk about APT activity in practical terms. Who are these threat actors? What are they actually doing? And most importantly, what can you realistically do about it? These are the questions I hear from security teams, and they deserve straight answers.

The APT threat is real, but it is not hopeless. Organizations that understand the threat and invest in appropriate defenses are significantly better off than those that do not. This post is about building that understanding and translating it into action.""",
    ],
    
    "Ransomware": [
        """Ransomware has become the most talked-about cyber threat for good reason. It is visible, it is damaging, and it is happening constantly. Every day, organizations large and small find themselves locked out of their own systems, facing demands for payment in cryptocurrency.

But ransomware today is not what it was five years ago. The attacks have become more sophisticated, the criminals more organized, and the stakes much higher. What used to be opportunistic attacks against whoever happened to click the wrong link have evolved into carefully planned operations targeting specific organizations with deep pockets.

I want to explain how modern ransomware operations actually work, because understanding the threat is the first step toward defending against it. This is not just about malware that encrypts files. It is about criminal organizations that have refined their tactics over years and continue to adapt to whatever defenses we put up.""",

        """If you have been paying attention to cybersecurity news, you know that ransomware is everywhere. Hospitals, schools, cities, manufacturers, law firms. No sector seems immune. The criminals behind these attacks have built a genuine industry, complete with customer service, affiliate programs, and technical support.

The financial impact is staggering. Ransom demands routinely reach into the millions. Recovery costs often exceed the ransom itself. And the disruption to operations can last weeks or months. For some organizations, a ransomware attack is an existential threat.

This post breaks down what we are seeing with ransomware right now. I will cover how the attacks work, why they are so effective, and what you can do to protect your organization. The threat is serious, but there are concrete steps that make a real difference.""",

        """Getting hit with ransomware is one of the worst experiences an organization can have. I have talked to IT teams who have been through it, and the stories are always stressful. The panic when systems start going down. The difficult conversations with leadership. The agonizing decisions about whether to pay.

This post is about helping you avoid being in that position. I will explain how ransomware attacks typically unfold, what makes some organizations more vulnerable than others, and what you can do now to reduce your risk. The threat is real, but it is not inevitable.

The ransomware landscape keeps evolving, and defenders need to evolve with it. What worked a year ago may not be sufficient today. Let me share what I am seeing and what it means for your security strategy.""",
    ],
    
    "Vulnerability": [
        """Every piece of software has bugs. That is just reality. But some bugs are worse than others, and the ones that attackers can exploit to break into systems are what we call vulnerabilities. Managing these vulnerabilities is one of the core challenges of cybersecurity.

The problem is that there are too many vulnerabilities to patch them all immediately. New ones are discovered every day, and most organizations simply do not have the resources to address everything at once. So we have to prioritize. But how do you know which vulnerabilities actually matter for your environment?

This post tackles the vulnerability management challenge head-on. I will share frameworks for prioritization, discuss what current exploitation trends tell us, and provide practical guidance for making sense of the endless stream of CVEs and security advisories.""",

        """Patching feels like it should be simple. A vendor releases an update, you install it, problem solved. But anyone who has worked in IT knows it is never that straightforward. There are dependencies, compatibility issues, testing requirements, and change windows to consider.

Meanwhile, attackers are watching the same vulnerability disclosures you are, and they move fast. The window between when a vulnerability becomes public and when exploitation begins is getting shorter every year. This creates real tension between the need for careful testing and the urgency of getting patches deployed.

In this post, I want to discuss vulnerability management in realistic terms. Not the ideal world where everything gets patched immediately, but the real world where you have to make hard choices about where to focus limited resources.""",

        """Vulnerability management is one of those topics where the theory sounds simple but the practice is incredibly difficult. You identify vulnerabilities, you prioritize them, you patch them. Easy, right? Except that most organizations have thousands of systems running software from hundreds of vendors, and new vulnerabilities are published constantly.

I have seen organizations struggle with this for years, and the ones that succeed usually share some common approaches. This post is about those approaches and how to think about vulnerability management in a way that actually reduces risk rather than just checking boxes.

The goal is not perfect patching. That is not achievable. The goal is smart prioritization that addresses the vulnerabilities most likely to be exploited against your specific environment.""",
    ],
    
    "Supply Chain": [
        """When we think about security, we usually focus on our own systems and our own people. But modern organizations depend on a web of vendors, software libraries, and service providers. An attack on any of these can become an attack on you, even if your own defenses are solid.

Supply chain attacks exploit this trust. Instead of attacking you directly, an adversary compromises something you depend on and uses that access to reach you. It is an efficient approach from the attacker's perspective because compromising one popular component can provide access to thousands of downstream victims.

This post examines the supply chain threat and what organizations can do about it. The challenge is real, but it is not insurmountable. Understanding where your dependencies lie is the first step toward managing the associated risks.""",

        """You probably use hundreds or thousands of third-party components in your organization without even knowing it. Open source libraries, SaaS applications, managed services, hardware from overseas manufacturers. Each of these represents a potential point of failure if something goes wrong.

The supply chain security conversation has gotten a lot of attention after some high-profile incidents, and for good reason. But many organizations still do not have a clear picture of what their supply chain actually looks like or how to assess the risks it introduces.

I want to help you think through the supply chain challenge in practical terms. What are the real risks? How do attacks actually happen? And what can you do to reduce your exposure without bringing operations to a halt?""",

        """Trust is fundamental to how technology works. You trust that the software you download does what it claims to do. You trust that the vendor updating your systems is actually the vendor. You trust that the open source library your developers imported is not malicious.

Supply chain attacks target this trust directly. When that trust is violated, the consequences can be severe and widespread. This post examines how supply chain attacks work, what we have learned from recent incidents, and how organizations can better protect themselves.

The supply chain problem is not going away. If anything, our increasing dependence on interconnected systems makes it more pressing. Understanding the threat is essential for anyone responsible for organizational security.""",
    ],
    
    "Threat Actor": [
        """Behind every cyber attack is a person or group with motivations, capabilities, and patterns of behavior. Understanding who these threat actors are and how they operate can help defenders anticipate and counter their activities.

The threat actor landscape is diverse. You have nation-state groups conducting espionage, criminal organizations running ransomware operations, hacktivists pursuing ideological goals, and individuals looking to make money or cause mischief. Each type of actor presents different challenges and requires different defensive approaches.

This post profiles the threat actor landscape as it exists today. By understanding who might target your organization and why, you can make better decisions about where to focus your security investments.""",

        """Cybersecurity is often discussed in technical terms, focusing on vulnerabilities, malware, and network traffic. But at its core, it is about people trying to stop other people from doing harmful things. Understanding the humans on the other side of the keyboard is essential for effective defense.

Different threat actors pose different risks. A financially motivated criminal gang operates differently than a nation-state intelligence service, and both differ from a lone insider with a grudge. Knowing who you are defending against shapes how you should defend.

In this post, I break down the major categories of threat actors and what makes each one tick. This context helps translate generic security advice into specific priorities for your situation.""",

        """Knowing your enemy is one of the oldest principles of conflict, and it applies to cybersecurity as much as anywhere else. The more you understand about who might attack you and why, the better prepared you can be to defend yourself.

The threat actor ecosystem is constantly evolving. Groups emerge, evolve, and sometimes disappear. Techniques that work get adopted widely. Understanding these dynamics helps defenders stay ahead of the curve.

This post examines the current threat actor landscape and what it means for organizational security. Whether you are worried about nation-states, criminals, or something else entirely, understanding your adversaries is fundamental to effective defense.""",
    ],
    
    "Industrial Control": [
        """Industrial control systems keep our power on, our water clean, and our factories running. These systems were designed for reliability and safety, often decades ago, when cybersecurity was not a significant concern. Now they face threats from sophisticated adversaries who understand both the technology and its critical importance.

The stakes in OT security are different from traditional IT. When things go wrong, the consequences can be physical, affecting safety, the environment, and public health. This reality shapes how we need to think about protecting these systems.

This post examines the current threat landscape for industrial control systems and what organizations operating critical infrastructure can do to improve their security posture.""",

        """If you work in critical infrastructure, you know that operational technology security is a different world from traditional IT security. The equipment is different, the priorities are different, and the consequences of getting it wrong are different too.

I have spent time with OT security teams at utilities and manufacturing facilities, and they face challenges that most IT security professionals never encounter. Legacy systems that cannot be patched. Safety concerns that limit what changes can be made. And increasing pressure from threats that were once considered theoretical.

This post addresses the ICS security challenge in practical terms. What are the real threats? What actually works for defense? And how do you balance security with the operational requirements that cannot be compromised?""",

        """The convergence of IT and OT networks has been happening for years, driven by the benefits of data sharing and remote management. But this convergence has also created new pathways for attackers to reach systems that were once isolated.

Critical infrastructure has become an attractive target for nation-state actors and, increasingly, for criminal groups as well. The potential for disruption to essential services makes these systems high-value targets.

This post examines where ICS security stands today and what organizations can do to protect their operational technology. The challenges are real, but progress is possible for organizations that approach the problem thoughtfully.""",
    ],
    
    "Cloud Security": [
        """Moving to the cloud changes everything about how you think about security. The perimeter you used to defend no longer exists. Your data sits on infrastructure you do not control. And the pace of change is faster than anything traditional IT had to deal with.

Cloud security is not just about applying old practices to new technology. It requires rethinking fundamental assumptions about access control, network security, and data protection. Organizations that treat cloud like just another data center often learn this lesson the hard way.

This post covers the essential elements of cloud security and the mistakes I see organizations make most often. The cloud can be very secure when configured properly. The challenge is knowing what properly means.""",

        """Cloud computing has transformed how organizations operate, but it has also introduced new security challenges that many teams are still learning to address. Misconfigurations, identity management issues, and shared responsibility confusion continue to drive cloud security incidents.

The good news is that cloud environments can be very secure when configured properly. The challenge is knowing what properly means in a rapidly evolving landscape with hundreds of services and features.

This post walks through the fundamentals of cloud security and provides practical guidance for avoiding common pitfalls. Whether you are just starting your cloud journey or well along the way, these principles apply.""",

        """Every organization I talk to is somewhere on their cloud journey. Some are fully cloud-native, others are in the middle of migration, and some are just starting to explore what cloud means for them. Regardless of where you are, security needs to be part of the conversation.

Cloud providers invest heavily in security, but they cannot do everything for you. The shared responsibility model means that how you configure and use cloud services determines much of your actual security posture.

This post explains where cloud security responsibilities lie and how to meet them. The cloud offers tremendous benefits, but realizing them securely requires understanding the new rules of the game.""",
    ],
    
    "Defense": [
        """Security is often discussed in terms of the threats we face, but ultimately what matters is what we do about them. Building effective defenses is hard work that requires understanding both the threat landscape and your own environment.

There is no silver bullet in security. No single product or practice that makes everything safe. Defense is about layers, trade-offs, and continuous improvement. This post focuses on defensive strategies that actually work, based on what organizations are doing successfully.

The goal is practical guidance you can apply, not theoretical frameworks that sound good but do not translate to reality.""",

        """I spend a lot of time studying threats, but I am ultimately more interested in defense. Understanding attacks matters, but only because it helps us build better protections. The goal is not to be an expert on threats. The goal is to keep our organizations safe.

This post is about defensive practices that make a real difference. Not theoretical security or compliance checkbox exercises, but actual improvements that reduce the likelihood and impact of attacks.

Security is fundamentally about making good decisions with limited resources. These are the decisions that matter most and how to approach them.""",

        """The security industry produces a constant stream of threat intelligence, new products, and best practice frameworks. It can be overwhelming to figure out what actually matters and where to invest your limited resources.

I want to cut through some of that noise and talk about defensive fundamentals that consistently make organizations more secure. These are not trendy or exciting, but they are effective.

Security is about doing the basics well, consistently, over time. This post covers what those basics are and how to implement them in ways that actually work.""",
    ],
}


# =============================================================================
# BACKGROUND PARAGRAPHS - Context in plain language (~400-500 words each)
# =============================================================================

BACKGROUND_PARAGRAPHS = {
    "APT Activity": [
        """To understand current APT activity, it helps to know how we got here. State-sponsored hacking is not new. Governments have been using computers for espionage since there were computers worth hacking. What has changed is the scale, sophistication, and boldness of these operations.

Early nation-state hackers targeted military and government systems primarily. Today, the targeting has expanded dramatically. Intellectual property in commercial companies, research at universities, personal information of dissidents, infrastructure that could be disrupted during conflict. Everything is potentially in scope.

The professionalization of these operations is striking. APT groups operate like well-funded development teams, with division of labor between those who find vulnerabilities, those who write exploits, those who conduct operations, and those who maintain infrastructure. They have quality assurance processes and learn from their mistakes.

Public attribution has become more common, with governments naming specific groups and sometimes indicting individuals. This has not stopped the activity, but it has provided valuable intelligence about who is doing what. Security researchers and government agencies now track dozens of named APT groups with documented histories and signatures.

The geopolitical context matters. Cyber operations reflect real-world tensions between nations. When relations deteriorate, cyber activity often increases. Understanding this context helps predict where threats might emerge and what sectors might be targeted.""",

        """The APT landscape today reflects geopolitical tensions that have been building for years. Major cyber powers have developed significant offensive capabilities, and they use them regularly to advance national interests.

China, Russia, North Korea, and Iran are most frequently named in public attributions, but they are not the only players. Many countries have developed or acquired cyber capabilities, and the proliferation of commercial hacking tools has lowered the barrier to entry.

What makes APTs particularly challenging is their persistence. Unlike criminals who might move on if initial attacks fail, state-sponsored groups are patient. They will try multiple approaches over extended periods. If they get kicked out of a network, they often try to get back in.

The goals of these groups vary. Intelligence collection is the most common objective, but we have also seen sabotage, intellectual property theft, financial gain, and what appears to be pre-positioning for potential future operations against critical infrastructure.

Recent years have seen increased boldness in APT operations. Attacks that would once have been kept quiet are now acknowledged. Operations that might have caused international incidents are conducted with apparent confidence that consequences will be limited. This emboldening trend is concerning for defenders.""",
    ],
    
    "Ransomware": [
        """Ransomware has existed for decades, but the modern ransomware era really began around 2016 with the rise of cryptocurrency and the refinement of encryption techniques. These developments solved two problems that had limited earlier ransomware: how to collect payments anonymously and how to reliably lock victims out of their data.

The business model evolved rapidly from there. Early ransomware cast a wide net, hitting whoever clicked the wrong link and demanding relatively small ransoms. Today's operations are targeted and professional, with attackers spending weeks inside networks before deploying ransomware at the worst possible moment.

The affiliate model transformed the ecosystem. Ransomware developers create and maintain the malware while affiliates conduct the actual attacks. This division of labor lets both sides specialize and scale their operations. It also makes attribution and disruption more difficult.

Double extortion changed the calculus for victims. When attackers just encrypted files, having good backups was often enough. Now they steal data first and threaten to publish it. Even organizations with excellent backup practices face difficult decisions when sensitive data is at risk.

Law enforcement has had some notable successes against ransomware operators, but new groups emerge to replace those that are disrupted. The fundamental economics continue to favor the attackers as long as victims keep paying.""",

        """The ransomware problem has gotten worse despite significant attention and resources devoted to addressing it. Law enforcement has had some notable successes, taking down infrastructure and arresting operators. But new groups emerge to replace those that are disrupted.

Several factors sustain the ransomware ecosystem. Cryptocurrency makes payments possible across borders without traditional financial system involvement. Jurisdictional challenges protect operators in countries that do not cooperate with Western law enforcement. And the simple economics work in the attackers' favor, with potential payouts in the millions against relatively modest operational costs.

Organizations of all sizes and sectors have been affected. Small businesses without dedicated security teams. Large enterprises with sophisticated defenses. Schools, hospitals, governments, manufacturers. If there is data worth holding hostage, someone will try.

The human cost is often overlooked in discussions of ransomware. IT teams work around the clock trying to recover. Employees cannot do their jobs. Customers are affected. In healthcare settings, patient care can be compromised. These are not abstract impacts.

The professionalization of ransomware operations continues. Customer service for victims. Negotiation specialists. Quality assurance for malware. These criminal enterprises operate with a level of sophistication that rivals legitimate businesses.""",
    ],
    
    "Vulnerability": [
        """Software vulnerabilities are inevitable given the complexity of modern systems. Millions of lines of code written by thousands of developers, often under deadline pressure, using libraries and frameworks they did not write. It would be surprising if there were not bugs.

What has changed is how quickly vulnerabilities are discovered and exploited. Security researchers, both independent and employed by vendors, continuously probe software for flaws. Bug bounty programs have created financial incentives to find and report vulnerabilities. And attackers do their own research, looking for weaknesses they can exploit.

The vulnerability disclosure ecosystem has matured over the years. Coordinated disclosure processes give vendors time to develop patches before vulnerabilities are made public. CVE identifiers provide a common vocabulary for discussing specific issues. And resources like the National Vulnerability Database aggregate information to help organizations understand their exposure.

But the sheer volume of vulnerabilities overwhelms many organizations. Thousands of new CVEs are published every year. Most security teams cannot possibly address them all quickly. This creates an ongoing challenge of prioritization and risk management.

The economics of vulnerability discovery and exploitation continue to evolve. Bug bounty payouts have increased, creating stronger incentives for researchers to report rather than exploit. But the black market for vulnerabilities remains active, and zero-day exploits command premium prices.""",

        """The race between disclosure and exploitation keeps getting faster. It used to be that organizations had weeks or months after a vulnerability was published to patch it. Now that window is often days, and for particularly valuable vulnerabilities, exploitation can begin within hours.

This acceleration reflects several trends. Attackers monitor the same security advisories and mailing lists that defenders do. Proof of concept code is often published alongside vulnerability details. And automated scanning tools can quickly identify vulnerable systems across the internet.

Edge devices and network appliances have become particularly attractive targets. These systems sit at the perimeter, are often internet-facing, and historically received less security scrutiny than endpoints. Successful exploitation can provide access to internal networks without having to get past other defenses.

The patching challenge is not just technical. It involves change management, testing, coordination, and sometimes difficult trade-offs between security and availability. Many organizations patch more slowly than they should not because they are unaware of vulnerabilities but because the process is complicated.

Prioritization frameworks like EPSS and the CISA Known Exploited Vulnerabilities catalog help organizations focus on what matters most. But implementing effective vulnerability management remains one of the persistent challenges in security.""",
    ],
    
    "Supply Chain": [
        """Modern software development depends on a vast ecosystem of shared components. Open source libraries, commercial SDKs, cloud services, APIs. No organization builds everything from scratch. This reuse creates efficiency but also creates risk when any of those components are compromised.

The software supply chain has become a target because of its leverage. Compromise one widely-used component, and you potentially gain access to every organization that uses it. For attackers, this is an attractive return on investment compared to compromising targets one at a time.

Several high-profile incidents have demonstrated the potential impact. Compromised build systems at software vendors led to malicious updates distributed to thousands of customers. Malicious code inserted into open source packages affected countless applications that depended on them. Third-party breaches exposed data from organizations that were not directly attacked.

Understanding supply chain risk requires visibility into what you actually depend on. Many organizations do not have complete inventories of their software components, especially in code written by developers who pull in libraries without formal tracking. You cannot protect what you do not know about.

The supply chain security challenge extends beyond software to hardware and services. Physical components manufactured overseas, cloud services operated by third parties, managed security providers with access to your environment. Each dependency is a potential point of failure.""",

        """The open source ecosystem presents particular challenges for supply chain security. Open source software powers much of the modern internet and is embedded in nearly every application. The code is often high quality and well-maintained, but it is also a target.

Many open source projects are maintained by small teams or even individuals with limited resources. They do not have security teams reviewing every contribution. And the mechanisms that make open source collaboration possible, like public repositories and package managers, can also be exploited by attackers.

Typosquatting, where malicious packages are published with names similar to popular legitimate packages, has become common. Developers who mistype a package name might inadvertently install malware. Account takeovers of package maintainers can lead to malicious updates being pushed to existing trusted packages.

Build systems and CI/CD pipelines are another attack surface. If attackers can compromise the systems that build and deploy software, they can inject malicious code without touching source repositories. This type of attack is harder to detect and can affect all software produced by the compromised build system.

Organizations are slowly improving their supply chain security practices, but progress is uneven. Software bills of materials, dependency scanning, and vendor assessment programs are becoming more common, but many organizations are still in early stages.""",
    ],
    
    "Threat Actor": [
        """The cybersecurity community tracks threat actors using various naming conventions, which can be confusing. APT numbers, animal names, element names, and vendor-specific designations all refer to groups identified through analysis of their activities. These names represent clusters of related activity, not necessarily single organizations.

Attribution is challenging and imperfect. Analysts examine technical indicators, targeting patterns, operational timing, tool overlap, and sometimes intelligence from other sources to group activities and make assessments about who is responsible. These assessments are probabilistic, not certain.

Understanding threat actor categories helps with prioritization. Nation-state actors have different resources, capabilities, and objectives than financially motivated criminals. Hacktivists operate differently than either. The defenses most effective against one type may not be optimal against another.

The threat actor landscape is also dynamic. Groups evolve their techniques, rebrand after exposure, collaborate with each other, and sometimes disappear. Tracking these changes is ongoing work that requires sustained attention.

Public reporting on threat actors has increased significantly, providing defenders with valuable intelligence. Government advisories, vendor research, and information sharing communities all contribute to collective understanding of who is doing what.""",

        """Financial motivation drives a large portion of cyber threat activity. Criminal groups pursue ransomware, business email compromise, credential theft, and other schemes that convert network access into money. The global nature of the internet lets these criminals target victims anywhere while operating from jurisdictions with limited law enforcement cooperation.

The cybercrime ecosystem has become highly specialized. Different actors focus on different phases of operations. Initial access brokers compromise networks and sell access. Malware developers create and maintain tools. Operators conduct the actual attacks. Money launderers clean the proceeds. This division of labor makes operations more efficient and investigation more complicated.

Nation-state actors have different motivations but sometimes employ similar techniques. Intelligence collection, intellectual property theft, and strategic positioning are common goals. Some nations also use cyber operations for financial gain, blurring the line between state-sponsored and criminal activity.

Hacktivism remains a factor, though its prominence has waxed and waned over the years. Ideologically motivated attackers pursue targets aligned with their causes, whether political, environmental, or social. Their technical sophistication varies widely, from simple defacement to significant data breaches.

Insider threats, both malicious and negligent, round out the threat actor landscape. The access that legitimate users have makes them potentially dangerous if they become adversarial or are socially engineered by external attackers.""",
    ],
    
    "Industrial Control": [
        """Industrial control systems were designed for a different era. Reliability, safety, and efficiency were the priorities. Security was addressed primarily through physical isolation, keeping operational technology networks separate from corporate IT and the internet.

That isolation has eroded over time. The benefits of connectivity, including remote monitoring, centralized management, and data analytics, drove organizations to link OT and IT networks. This convergence has been happening for years and is unlikely to reverse.

The result is that systems designed without security as a primary consideration now face threats from sophisticated adversaries. Patching is difficult or impossible for some legacy systems. Security tools designed for IT environments may not work well in OT contexts. And the consequences of security failures can be far more severe than data loss.

Critical infrastructure sectors, including energy, water, transportation, and manufacturing, face elevated threat levels. Nation-state actors have demonstrated interest and capability in targeting these systems. Criminal ransomware operators have realized that operational disruption creates strong payment pressure.

Regulatory frameworks for critical infrastructure security are evolving but remain inconsistent. Some sectors have mandatory requirements, others rely on voluntary guidelines. Organizations must navigate this complex landscape while addressing real security gaps.""",

        """The IT and OT security divide reflects real differences in priorities and constraints. In IT, confidentiality often leads the CIA triad. In OT, availability and integrity matter more because systems control physical processes. Downtime is not just inconvenient; it can stop production or compromise safety.

Change management in OT environments is necessarily more conservative. Patching a server that runs a website is very different from patching a controller that runs a chemical process. Testing requirements are more rigorous. Maintenance windows may be limited to annual shutdowns. And the risk of breaking something critical is higher.

These constraints make OT security challenging but not impossible. The key is adapting security practices to OT realities rather than simply applying IT approaches. This means understanding what actually runs in OT environments, what the real risks are, and what controls are feasible given operational requirements.

The security community has developed OT-specific frameworks and guidance that address these unique challenges. NIST, ICS-CERT, and sector-specific organizations provide resources tailored to operational technology environments.

Progress is being made, but the pace is often slower than security teams would like. Budgets, organizational culture, and the long lifecycle of OT equipment all present obstacles. Patient, persistent effort is required to improve OT security posture.""",
    ],
    
    "Cloud Security": [
        """Cloud computing represented a fundamental shift in how organizations build and operate IT infrastructure. Instead of buying and managing hardware, you consume computing resources as a service. This model offers flexibility, scalability, and often cost advantages, but it also changes the security equation.

The shared responsibility model is central to cloud security. Cloud providers secure the infrastructure, the physical data centers, the hypervisors, and the hardware. Customers are responsible for securing what they build on top of that infrastructure, their configurations, their applications, and their data.

Misunderstanding this division of responsibility is one of the most common sources of cloud security problems. Organizations that assume the cloud provider handles everything end up with exposed storage buckets, overly permissive access policies, and vulnerable configurations.

The pace of change in cloud environments adds to the challenge. Cloud providers constantly release new services and features. Cloud-native architectures involve ephemeral resources that spin up and down dynamically. Security teams must adapt to monitoring and protecting environments that look nothing like traditional data centers.

Cloud security tools and practices have matured significantly, but adoption remains uneven. Many organizations are still applying on-premises approaches to cloud environments, missing the need for cloud-native security capabilities.""",

        """Identity has become the primary security boundary in cloud environments. Traditional network perimeters provided a clear inside and outside. In the cloud, resources might be accessed from anywhere, and the network itself is managed by the provider.

This shift puts enormous weight on identity and access management. Who can access what resources? How are they authenticated? What happens if credentials are compromised? These questions are central to cloud security in a way they were not for on-premises environments.

The proliferation of credentials in cloud environments creates attack surface. OAuth tokens, API keys, service accounts, and IAM roles all provide access paths that attackers can target. Managing this credential sprawl is essential but often neglected.

Cloud-native threats have evolved alongside cloud adoption. Attackers understand cloud services and how to exploit them. They target cloud-specific weaknesses like instance metadata services, public storage buckets, and overprivileged identities. Defending against these threats requires cloud-specific security knowledge.

Multi-cloud and hybrid environments add complexity. Different providers have different security models and tools. Maintaining consistent security across multiple environments requires careful planning and often additional tooling.""",
    ],
    
    "Defense": [
        """The evolution of cyber threats has driven corresponding evolution in defensive approaches. Perimeter security gave way to defense in depth. Signature-based detection yielded to behavioral analysis. And the assumption of breach has replaced the hope of prevention.

Modern security programs try to balance multiple objectives. Prevention matters because every attack you stop is one you do not have to respond to. Detection matters because prevention is imperfect. Response matters because how quickly you contain an incident affects the damage. And recovery matters because sometimes things go wrong despite your best efforts.

The security industry produces an overwhelming array of tools and technologies. Every category seems to have dozens of vendors with overlapping claims. Navigating this landscape requires clear understanding of your own needs and realistic expectations about what any tool can actually do.

Process and people matter at least as much as technology. The best security tools are ineffective if they are not properly configured and monitored. Detection capabilities are useless if there is no one to investigate alerts. And incident response fails without planning and practice.

Security culture affects outcomes as much as security technology. Organizations where security is everyone's responsibility fare better than those where it is siloed in a security team. Building this culture is slow work but pays dividends.""",

        """Security measurement remains a persistent challenge. How do you know if your security program is working? Traditional metrics like patch coverage or training completion provide some signal, but they do not directly measure risk or outcomes.

Mature security programs are experimenting with more meaningful metrics. Time to detect and contain incidents provides insight into detection and response capabilities. Tabletop exercises and red team engagements test defenses against realistic attacks. And tracking near-misses and close calls can reveal weaknesses before they are exploited.

Security is ultimately about risk management. Perfect security is unachievable and would be unaffordable even if it were possible. The goal is to reduce risk to acceptable levels given available resources and organizational risk tolerance.

This requires ongoing assessment and adjustment. The threat landscape changes. Your environment changes. What was appropriate last year may not be appropriate now. Continuous improvement is not just a buzzword; it is a necessity for effective security.

Resource constraints are a reality for almost every security program. Doing everything is not possible. Making smart choices about where to focus limited resources is perhaps the most important skill for security leaders.""",
    ],
}


# =============================================================================
# TECHNICAL PARAGRAPHS - How attacks work (~500-600 words each)
# =============================================================================

TECHNICAL_PARAGRAPHS = {
    "APT Activity": [
        """Let me walk through how a typical APT operation unfolds based on what we know from public reporting. The details vary between groups and targets, but the general pattern is consistent.

Initial access usually comes through one of a few vectors. Spearphishing remains popular because it works. A carefully crafted email with a malicious attachment or link, targeted at someone with access to what the attackers want. Exploitation of internet-facing systems is another common path, particularly VPNs, email servers, and web applications with known vulnerabilities.

Once inside, the priority is establishing persistence. The attackers want to make sure they can maintain access even if the initial entry point is discovered and closed. They deploy backdoors, often multiple ones, in locations throughout the network. These might be scheduled tasks, modified services, web shells, or implants hidden in legitimate software.

Reconnaissance follows. The attackers learn the network layout, identify high-value targets like domain controllers and file servers, and locate the data they are after. This phase can take weeks or months. The attackers are careful to avoid triggering alerts, often conducting activities during business hours when admin activity is normal.

Lateral movement lets attackers spread through the network. They harvest credentials, exploit trust relationships between systems, and gradually gain access to additional resources. Living-off-the-land techniques, using built-in system tools rather than custom malware, help them blend in with legitimate activity.

Data exfiltration is typically the final objective for espionage operations. The stolen data is compressed, encrypted, and sent to attacker-controlled infrastructure. This might happen slowly to avoid detection, or quickly if the attackers believe they are about to be discovered.""",
    ],
    
    "Ransomware": [
        """Modern ransomware attacks are not smash-and-grab operations. They are methodical intrusions that unfold over days or weeks before the actual ransomware deployment. Understanding this timeline is important for both prevention and response.

Initial access looks similar to other intrusion types. Phishing emails, exploitation of vulnerable internet-facing systems, or purchased access from initial access brokers. Attackers buy credentials or network access on criminal forums, eliminating the need to break in themselves.

Once inside, the attackers take time to understand the environment. They identify critical systems, locate backup infrastructure, and assess what data might be valuable for extortion. They are looking for ways to maximize impact and pressure.

Disabling security controls is a priority before deployment. Attackers target antivirus software, disable Windows Defender, and may even uninstall security agents. This preparation significantly increases the chances of successful encryption.

Data exfiltration happens during the pre-deployment phase. Attackers identify sensitive files, customer data, intellectual property, financial records, and copy them to external infrastructure. This stolen data becomes leverage for double extortion.

The actual ransomware deployment is usually scheduled for maximum impact. Nights or weekends when response capability is reduced. The beginning of a busy period when downtime is most painful. The encryption itself happens quickly once initiated, using techniques like intermittent encryption to maximize speed.

After encryption, the ransom demand arrives. Victims are directed to a portal or given contact information to negotiate. Some operators provide proof that decryption works and stolen data exists. Negotiation often follows, with attackers sometimes adjusting demands based on victim circumstances.""",
    ],
    
    "Vulnerability": [
        """Vulnerability exploitation is often simpler than people imagine. Once a working exploit exists, using it against a vulnerable system is usually straightforward. The complexity is in finding the vulnerability and developing the exploit, not in using it.

Network-based exploitation targets services listening on network ports. The attacker sends specially crafted data that the vulnerable service mishandles, leading to arbitrary code execution, authentication bypass, or information disclosure. Edge devices like VPNs and firewalls are frequent targets because they are internet-facing and often have direct access to internal networks.

Web application vulnerabilities are another major category. Injection attacks, authentication flaws, and access control failures let attackers steal data, impersonate users, or execute code on web servers. These vulnerabilities are common despite being well-understood because secure development is hard.

Client-side exploitation targets software that processes attacker-controlled content. Browsers, PDF readers, and document applications have all been vectors for delivering malware. The attacker provides a malicious file or webpage, and the vulnerable application does the rest.

Exploitation chains combine multiple vulnerabilities to achieve greater impact. A lower-severity vulnerability might provide initial code execution that is then used to exploit a privilege escalation vulnerability. These chains are particularly valuable because they can compromise fully-patched systems if the individual vulnerabilities are not yet known.

Post-exploitation tools let attackers leverage their initial access. Frameworks like Cobalt Strike, originally developed for penetration testing, are widely used by both criminal and state-sponsored actors to conduct operations after initial exploitation.

The window between disclosure and exploitation continues to shrink. For high-profile vulnerabilities, working exploits may appear within hours of public disclosure. Defenders have less and less time to patch before active exploitation begins.""",
    ],
    
    "Supply Chain": [
        """Supply chain attacks exploit the trust relationships that make software ecosystems work. When you install software from a vendor or import a library into your code, you are trusting that the code does what it claims and nothing more. Attackers target this trust.

Compromising build systems is one approach. If attackers gain access to the systems that compile and package software, they can inject malicious code into legitimate products. Customers receive updates through normal channels with no indication that anything is wrong.

Package manager attacks target the distribution of code libraries. Publishing malicious packages with names similar to popular legitimate ones catches developers who mistype. Compromising maintainer accounts allows pushing malicious updates to existing trusted packages.

Open source contributions can introduce vulnerabilities. Most open source projects welcome contributions, and review processes vary in rigor. A sophisticated attacker might submit seemingly innocent changes over time that create exploitable conditions.

Third-party service compromises affect customers who rely on those services. If attackers compromise a vendor, they may gain access to customer data or credentials. Cloud services, managed security providers, and IT service companies are attractive targets because of their access to many organizations.

Detection is challenging because supply chain attacks use trusted channels. The malicious code arrives through the same update mechanisms as legitimate updates. Traditional security tools may not flag it because it comes from an expected source with proper signatures.

The best defense is layered. Verify software integrity where possible. Monitor for unusual behavior from trusted applications. Limit the access and privileges granted to third-party software. And maintain visibility into what dependencies your organization actually uses.""",
    ],
    
    "Threat Actor": [
        """Understanding threat actor operations helps defenders anticipate behavior and prioritize defenses. Different types of actors operate differently, and these patterns can inform security decisions.

Nation-state actors typically have dedicated teams, substantial resources, and specific objectives aligned with national interests. They can afford to be patient, spending months on reconnaissance and carefully avoiding detection. They often have access to zero-day vulnerabilities and custom tools.

Criminal groups are profit-motivated, which shapes their operations. They invest in techniques that have good return on investment. Ransomware is popular because it works and scales. They operate more like businesses than military units, with concerns about costs and efficiency.

Initial access brokers specialize in gaining network access without conducting follow-on operations. They compromise targets through various means and then sell access to other criminal groups. This specialization lets each part of the criminal ecosystem focus on what they do best.

Threat actors continuously adapt to defensive improvements. Techniques that worked well become less effective as defenders develop countermeasures, so attackers develop new approaches. This creates an ongoing cycle that requires defenders to stay current.

Infrastructure management is a key operational concern. Attackers need command and control servers, staging infrastructure, and ways to receive stolen data. They balance operational security, using infrastructure that cannot be easily linked to them, against the need for reliable operations.

The tools threat actors use range from custom-developed malware to commercial software and open source frameworks. Many groups use the same tools, making attribution based solely on tools unreliable. Behavioral patterns and targeting often provide better indicators of who is behind an attack.""",
    ],
    
    "Industrial Control": [
        """Attacks on industrial control systems can take different forms depending on attacker objectives and capabilities. Some focus on disruption, while others aim for espionage or positioning for future operations.

IT-to-OT pivots are the most common attack path. Attackers first compromise corporate IT networks using conventional techniques, then work to find connections to operational technology environments. Engineering workstations, historians, and jump servers are often the bridge.

Direct ICS attacks require specialized knowledge but can be highly effective. Attackers who understand industrial protocols can send commands directly to controllers, potentially affecting physical processes. These attacks are rare but serious when they occur.

Ransomware has reached OT environments, sometimes intentionally and sometimes as collateral damage when IT encryption spreads to connected systems. The operational impact motivates payment even when data itself is not the primary concern.

Safety system targeting represents the most dangerous scenario. Safety instrumented systems exist to prevent dangerous conditions like overpressure, over-temperature, or chemical releases. Attacks that disable or manipulate these systems could cause physical harm.

The Purdue Model provides a framework for understanding ICS architecture and security zones. Different levels from physical processes up through enterprise networks have different security requirements and appropriate controls. Defending ICS environments requires understanding this layered architecture.

Legacy protocols in OT environments often lack authentication and encryption. This makes network-based attacks possible if attackers can reach the OT network. Segmentation between IT and OT is critical, but must be implemented carefully to avoid breaking necessary communications.""",
    ],
    
    "Cloud Security": [
        """Cloud attack techniques have evolved alongside cloud adoption. Attackers understand cloud services and target the weaknesses that cloud environments introduce.

Credential theft remains fundamental. Phishing for cloud credentials, stealing access tokens, and compromising developer workstations to obtain cloud access keys are all common techniques. Once attackers have valid credentials, they can access cloud resources directly.

Misconfiguration exploitation targets the errors that are common in complex cloud environments. Public storage buckets, overly permissive IAM policies, and exposed management interfaces all provide opportunities for attackers. Automated scanning tools constantly search for these weaknesses.

Instance metadata services can provide credential access. Cloud VMs can query local metadata services for information including temporary credentials. If an attacker gains code execution on a VM, they may be able to retrieve these credentials and access other cloud resources.

Privilege escalation in cloud environments exploits overly permissive policies. An attacker with limited access may find paths to greater privileges through policy misconfigurations, service accounts with excessive permissions, or exploitation of cloud service vulnerabilities.

Persistence in cloud environments looks different than on-premises. Attackers may create new users or roles, deploy backdoor applications, or modify automation to maintain access. Detecting these changes requires monitoring cloud control plane activity, not just workload behavior.

Data exfiltration from cloud environments can happen through multiple paths. Direct download, cloud-native sharing features, or staging through other cloud services. Organizations need visibility into data access patterns and egress controls.

Cloud-specific security tools are essential for protecting cloud environments. Traditional security tools designed for on-premises environments often cannot see or protect cloud resources effectively.""",
    ],
    
    "Defense": [
        """Building effective defenses requires understanding what you are protecting and what you are protecting against. Generic security measures have value, but the best defenses are tailored to specific risks.

Network segmentation limits lateral movement by restricting what systems can communicate with each other. Even if an attacker compromises one segment, they face additional barriers reaching other parts of the network. Proper segmentation requires understanding traffic patterns and business requirements.

Endpoint detection and response provides visibility into what happens on endpoints. Unlike traditional antivirus focused on known malware signatures, EDR tools can detect suspicious behaviors and provide data for investigation. The catch is that someone needs to actually investigate alerts.

Log collection and analysis underpin detection capability. You cannot detect what you cannot see. Collecting logs from systems, applications, and network devices creates the raw material for finding threats. But logs are only useful if they are analyzed, either by people or by security tools.

Identity and access management determines who can access what resources. The principle of least privilege, giving people only the access they need, limits the damage from compromised accounts. Multi-factor authentication makes credential theft less effective.

Incident response capability determines how quickly you contain threats once detected. Having playbooks, trained responders, and practiced procedures reduces the chaos when incidents occur. Tabletop exercises reveal gaps before real incidents expose them.

Backup and recovery ensure you can restore operations if other defenses fail. Backups must be tested, protected from ransomware, and available when needed. Recovery procedures should be documented and practiced.

Security awareness helps people recognize and avoid threats. Training should be relevant and practical, not checkbox exercises. People are often the last line of defense against social engineering attacks.""",
    ],
}


# =============================================================================
# IMPACT PARAGRAPHS (~350-400 words each)
# =============================================================================

IMPACT_PARAGRAPHS = [
    """The impact of these attacks extends beyond the immediate technical damage. Organizations that experience significant incidents face cascading consequences that can last months or years.

Operational disruption is often the most visible impact. Systems go offline, employees cannot work, and normal business processes stop. For some organizations, a few days of downtime is manageable. For others, particularly in healthcare, manufacturing, or logistics, even hours of disruption have serious consequences.

Financial costs add up quickly. There are direct costs like incident response services, legal fees, regulatory notifications, and sometimes ransom payments. But indirect costs often exceed the direct ones. Lost revenue during downtime, overtime for staff handling recovery, customers who leave, and increased costs for security improvements afterward.

Regulatory and legal consequences depend on what data was involved and what obligations apply. Healthcare organizations face HIPAA considerations. Financial services have their own requirements. Data protection laws like GDPR impose notification obligations and potential fines. Legal exposure from affected parties adds another dimension.

Reputational damage is hard to quantify but real. Customers, partners, and the public form opinions based on how organizations handle incidents. Transparent, competent response can actually enhance reputation, while bungled incidents erode trust. The long-term business impact of reputation changes is significant.

For individuals within affected organizations, incidents are stressful and career-affecting. IT teams work exhausting hours. Executives face difficult decisions with incomplete information. And sometimes, fairly or not, people lose their jobs. The human cost of cyber incidents deserves acknowledgment.""",

    """When we talk about attack impact, we need to be specific about what actually happens to affected organizations. Abstract discussions of risk do not capture the reality that these events create.

Business operations can grind to a halt. Email down. Files inaccessible. Production stopped. Customer-facing systems offline. For organizations without robust business continuity planning, there may be no workaround. People simply cannot do their jobs until systems are restored.

The recovery process is often longer than anyone expects. Getting systems back online is just the start. Investigating what happened, ensuring attackers are truly out, rebuilding trust in system integrity. Organizations that think they will be back to normal in a week often find it takes a month or more.

Financial impacts compound over time. The initial costs for response and recovery are just the beginning. Insurance premiums increase. Customers who lost trust take their business elsewhere. Investment in security improvements requires budget. Some organizations never fully recover financially from major incidents.

Leadership attention gets consumed by the incident. Executive teams that should be focused on strategy and growth instead spend weeks dealing with crisis. Board meetings become incident reviews. The opportunity cost of this diverted attention is real even if hard to measure.

The psychological toll on those involved is often underestimated. Security teams who feel they failed. IT staff working brutal hours. Employees who feel violated by data theft. These human impacts matter and affect organizational resilience going forward.""",
]


# =============================================================================
# RECOMMENDATION PARAGRAPHS (~450-500 words each)
# =============================================================================

RECOMMENDATION_PARAGRAPHS = [
    """Based on what we have covered, let me share some practical recommendations. I have organized these by timeframe to help with prioritization, recognizing that not everything can happen at once.

In the next few days, take a hard look at your exposure to the attack vectors we discussed. Do you have systems that might be vulnerable? Are you monitoring the right things? Are there obvious gaps you have been meaning to address? Now is the time.

Review your incident response readiness. If something happened tomorrow, would your team know what to do? Are contact lists current? Are playbooks documented and accessible? A quick tabletop exercise can reveal gaps you did not know existed.

Check your backups. Not just whether they exist, but whether you can actually restore from them. When was the last time you tested recovery? Are backups protected from the threats we discussed? Confidence in backups only counts if it is justified.

Over the next few weeks, brief your stakeholders on the threat landscape. Security decisions benefit from organizational understanding and support. Leadership that understands the risks makes better decisions about investments and priorities.

Evaluate your detection capabilities. Are you monitoring for the indicators and behaviors discussed in this post? Detection is only as good as your visibility. Gaps in logging or monitoring create blind spots that attackers exploit.

Longer term, invest in security improvements that address the fundamental weaknesses attackers exploit. This might mean better network segmentation, stronger identity controls, or improved security operations capabilities. These are not quick fixes, but they make a lasting difference.

Build relationships with others in your sector. Information sharing communities provide early warning about threats and insight into what others are seeing. The security community is stronger when organizations help each other.""",

    """Let me translate what we have discussed into concrete actions you can take to improve your security posture. These recommendations are based on what actually works, not theoretical best practices.

Start with visibility. You cannot defend what you cannot see. Make sure you are collecting logs from critical systems, network devices, and security tools. Review whether you have the visibility needed to detect the types of attacks we discussed.

Test your assumptions. Many organizations believe they would detect or recover from certain attacks but have not actually tested it. Tabletop exercises, red team engagements, and recovery drills reveal whether your confidence is warranted.

Prioritize based on actual risk. Not every vulnerability matters equally. Not every threat is relevant to your organization. Focus your limited resources on the things most likely to affect you. This requires understanding your own environment and the threat landscape.

Address the basics consistently. Patching, strong authentication, access control, network segmentation, backup. These fundamentals stop most attacks. Exotic threats are real, but most organizations are not exploited by zero-days. They are exploited by known vulnerabilities and stolen credentials.

Build response capability. Assume that prevention will sometimes fail and prepare accordingly. Know who to call, what to do first, and how to communicate. Practicing response before you need it dramatically improves outcomes when incidents occur.

Keep learning. The threat landscape evolves, and defenders need to evolve with it. Stay current through industry publications, information sharing communities, and training. The knowledge you have today will not be sufficient forever.

Make security part of how you operate, not a separate activity. The most effective security programs are integrated into normal business processes. Security that relies on perfect human behavior will fail. Security that is designed into systems and processes succeeds.""",
]


# =============================================================================
# CONCLUSION PARAGRAPHS (~200-250 words each)
# =============================================================================

CONCLUSION_PARAGRAPHS = [
    """The threat we have discussed today is real and active. Organizations are being affected right now, and the impact is significant. But this is not cause for despair. Effective defenses exist, and organizations that invest in security are better off than those that do not.

The recommendations I have shared are practical and achievable. Not everything needs to happen at once, but progress needs to start. Prioritize based on your specific situation and take concrete steps forward.

Security is a journey, not a destination. The threats will continue to evolve, and our defenses must evolve with them. What matters is steady improvement and realistic assessment of where we stand.

I will continue covering this topic as new information emerges. The security community benefits when we share knowledge and learn from each other. If you have insights or questions, I want to hear from you.

Stay safe out there.""",

    """We have covered a lot of ground in this post. The technical details matter, but what matters more is what you do with this information. Knowledge without action does not improve security.

I hope this post has given you a clearer picture of the threat and practical ideas for improving your defenses. The specific actions that make sense depend on your organization, but the principles apply broadly.

Security is fundamentally about making good decisions under uncertainty. We cannot eliminate risk, but we can manage it. We cannot prevent every attack, but we can reduce their likelihood and limit their impact.

The work of security is never done, but it is worthwhile. Every improvement makes your organization a harder target. Every incident you prevent is damage that does not happen.

Until next time, stay vigilant.""",

    """What I have shared today reflects my analysis of current threats and effective defenses. Your situation may differ, and you should adapt these recommendations to your specific context.

The cybersecurity field advances through shared learning. Public reporting, government advisories, and community discussion all contribute to collective understanding. We are stronger when we work together.

I encourage you to share what you learn with others in your field. An attack that is stopped at one organization because another shared warning is a win for everyone. The attackers share information. We should too.

Thank you for reading. I will be back with more analysis as the situation develops. In the meantime, focus on the fundamentals and make continuous progress.

Stay secure.""",
]


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

def generate_content_for_category(topic, category, intro_template=None, structure=None, is_trend=False):
    """
    Generate full post content for a category.
    
    Produces 2,300-3,000 words of paragraph-focused content in plain language.
    Includes anti-repetition protection via content state tracking.
    """
    import re
    
    state = load_content_state()
    
    mark_topic_used(topic, state)
    mark_category_used(category, state)
    
    # Select content blocks avoiding repetition
    intro_pool = INTRO_PARAGRAPHS.get(category, INTRO_PARAGRAPHS["Defense"])
    intro = select_from_pool(intro_pool, category, "intro", state)
    
    bg_pool = BACKGROUND_PARAGRAPHS.get(category, BACKGROUND_PARAGRAPHS["Defense"])
    background = select_from_pool(bg_pool, category, "background", state)
    
    tech_pool = TECHNICAL_PARAGRAPHS.get(category, TECHNICAL_PARAGRAPHS["Defense"])
    technical = select_from_pool(tech_pool, category, "technical", state)
    
    impact = random.choice(IMPACT_PARAGRAPHS)
    recommendations = random.choice(RECOMMENDATION_PARAGRAPHS)
    conclusion = random.choice(CONCLUSION_PARAGRAPHS)
    
    # Build content sections
    intro_html = f"""<section id="introduction">
<h2>Introduction</h2>
{intro}
</section>"""

    background_html = f"""<section id="background">
<h2>Background</h2>
{background}
</section>"""

    technical_html = f"""<section id="technical-breakdown">
<h2>Technical Breakdown</h2>
{technical}
</section>"""

    indicators_html = f"""<section id="what-i-found">
<h2>Key Indicators</h2>
<p>Based on public reporting and advisories, there are several indicators that organizations should monitor for. These are not exhaustive, and threat actors continuously adapt their techniques, but they provide a starting point for detection efforts. The key is building detection capabilities that can identify these patterns in your specific environment.</p>

<p>Network-based indicators include unusual outbound connections, particularly to newly registered domains or known malicious infrastructure. DNS queries from systems that do not normally make external requests deserve attention. Communication patterns that differ from baseline behavior, such as connections at unusual times or to unusual destinations, warrant investigation. Look for beaconing patterns where systems connect to external hosts at regular intervals, which often indicates command and control traffic.</p>

<p>On endpoints, look for evidence of the techniques described earlier. Unexpected processes, particularly those with administrative privileges, should trigger investigation. Modifications to scheduled tasks or services can indicate persistence mechanisms. Access to credential stores like LSASS or attempts to dump memory are red flags. Files appearing in unexpected locations or with unusual characteristics warrant examination. Pay attention to process injection, where legitimate processes spawn unusual child processes or load unexpected libraries.</p>

<p>Authentication and access patterns often reveal compromise. Service accounts used interactively, administrator accounts authenticating from new systems, or any accounts authenticating at unusual times should be investigated. Failed authentication attempts followed by success might indicate credential guessing or stuffing. Access to sensitive data repositories by accounts that do not normally need such access is concerning.</p>

<p>Behavioral patterns often provide the best detection opportunities even when specific technical indicators are absent. Bulk data access or unusual data movement patterns might indicate exfiltration staging. Large file compression or encryption activity outside of normal backup processes deserves scrutiny. Administrative tool usage from non-administrative workstations can indicate lateral movement.</p>

<p>Email and phishing indicators remain relevant for attacks that begin with social engineering. Watch for internal emails with unusual attachments, especially from compromised accounts sending to many recipients. Links to credential harvesting pages, particularly those mimicking internal systems, indicate active phishing. Users reporting suspicious emails provides valuable early warning if you have trained people to recognize and report them.</p>

<p>Changes to security controls themselves can indicate an attacker preparing for the final phase of their operation. Disabled antivirus, modified Windows Defender settings, or deleted security event logs all suggest someone is trying to operate undetected. Legitimate administrators rarely make these changes without documentation and approval.</p>

<p>Remember that indicators have a shelf life. What worked for detection last month may not work next month as attackers adapt. Detection capabilities need continuous refinement based on current threat intelligence. The goal is not to catch every possible indicator but to have enough coverage that attacker activity becomes visible somewhere in the kill chain.</p>
</section>"""

    attack_html = f"""<section id="attack-patterns">
<h2>Attack Patterns</h2>
<p>Understanding how attacks typically unfold helps with both prevention and detection. While every attack is different in its details, patterns emerge that defenders can use to anticipate and counter adversary behavior.</p>

<p>Initial access is the first challenge attackers must solve. They need to get a foothold in the target environment. The most common methods include phishing with malicious attachments or links, exploitation of internet-facing systems, and use of valid credentials obtained through prior compromise or purchase. Organizations with good perimeter defenses force attackers to use more sophisticated approaches, but determined adversaries usually find a way in eventually.</p>

<p>After initial access, attackers focus on establishing persistence and understanding the environment. This phase is often where detection opportunities exist. The attacker needs to take actions to maintain access and gather information, and these actions leave traces. Patient attackers may spend weeks in this phase, carefully avoiding detection while mapping the network and identifying valuable targets.</p>

<p>Credential harvesting is usually a priority once initial access is established. Attackers want to move beyond their initial compromised account to gain broader access. They target credential stores, memory dumps, cached credentials, and sometimes social engineering of help desk staff. With administrator credentials, most networks become much easier to traverse.</p>

<p>Lateral movement lets attackers spread through the network toward their objectives. Credential harvesting provides access to additional systems. Trust relationships between systems are exploited. Attackers often use legitimate administrative tools for movement to blend with normal activity. This phase continues until the attacker has access to what they want.</p>

<p>Defense evasion runs throughout the attack lifecycle. Attackers modify their behavior based on what defenses they encounter. They may disable security tools, clear logs, use encryption to hide their traffic, or time their activities to coincide with normal business operations. Sophisticated attackers test their tools against common security products before deploying them.</p>

<p>The final phase depends on attacker objectives. For espionage, it means data exfiltration. For ransomware, it means encryption deployment. For sabotage, it means disruption of operations. Understanding what attackers want helps predict what they will do once they have sufficient access.</p>

<p>The time from initial access to final objective varies enormously. Automated attacks might complete in minutes. Sophisticated ransomware operators typically spend days or weeks preparing before deployment. Nation-state espionage operations can maintain access for months or years. Knowing what type of adversary you face helps estimate how much time you have to detect and respond.</p>
</section>"""

    impact_html = f"""<section id="real-world-impact">
<h2>Real World Impact</h2>
{impact}
</section>"""

    recommendations_html = f"""<section id="recommendations">
<h2>My Recommendations</h2>
{recommendations}
</section>"""

    conclusion_html = f"""<section id="final-thoughts">
<h2>Final Thoughts</h2>
{conclusion}
</section>"""

    resources_html = """<section id="resources">
<h2>Resources</h2>
<p>For more information on the topics covered in this post, I recommend the following resources. These provide authoritative guidance and current information that complements what we have discussed. Staying informed about evolving threats and defenses is essential for effective security.</p>

<p>The Cybersecurity and Infrastructure Security Agency publishes advisories, alerts, and guidance that reflect current threat activity and best practices. Their Known Exploited Vulnerabilities catalog is particularly useful for prioritization, as it focuses on vulnerabilities that are actually being exploited in the wild rather than theoretical risks. CISA also provides sector-specific guidance that can help organizations understand threats relevant to their industry.</p>

<p>The MITRE ATT&CK framework provides a structured way to understand adversary techniques and map defensive capabilities. It has become a common language for discussing threats across the security community. Using ATT&CK to evaluate your detection coverage can reveal gaps and guide security investments. The framework is continuously updated based on observed adversary behavior.</p>

<p>Sector-specific Information Sharing and Analysis Centers provide threat intelligence tailored to particular industries. If one exists for your sector, joining it provides access to relevant information and community support. These organizations facilitate sharing between member organizations and often have relationships with government agencies that provide early warning about emerging threats.</p>

<p>Vendor security advisories and blogs often contain detailed technical analysis of specific threats. Following the security teams at major software vendors, cloud providers, and security companies provides insight into what they are seeing across their customer bases. This information can help you understand whether threats discussed in general terms actually apply to your environment.</p>

<ul class="reference-list">
<li><a href="https://www.cisa.gov/cybersecurity-advisories" target="_blank" rel="noopener noreferrer">CISA Cybersecurity Advisories</a></li>
<li><a href="https://attack.mitre.org/" target="_blank" rel="noopener noreferrer">MITRE ATT&CK Framework</a></li>
<li><a href="https://nvd.nist.gov/" target="_blank" rel="noopener noreferrer">National Vulnerability Database</a></li>
<li><a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" rel="noopener noreferrer">CISA Known Exploited Vulnerabilities</a></li>
</ul>
</section>"""

    # Combine all sections
    body = f"""{intro_html}

{background_html}

{technical_html}

{indicators_html}

{attack_html}

{impact_html}

{recommendations_html}

{conclusion_html}

{resources_html}"""

    # Calculate word count
    text_only = re.sub(r'<[^>]+>', '', body)
    word_count = len(text_only.split())
    
    reading_time = max(10, word_count // 200)
    
    excerpt = f"An in-depth look at {topic.lower()}. This post examines the current threat landscape, breaks down how attacks work, and provides practical recommendations for defenders."
    
    meta_description = f"{topic}: Analysis of attack techniques, real-world impact, and actionable defensive recommendations from Black Wing Dispatch."[:155]
    
    keywords = [
        category.lower().replace(" ", "-"),
        "cybersecurity",
        "threat-analysis", 
        "security",
        topic.split()[0].lower() if topic else "threat",
    ]
    
    save_content_state(state)
    
    return {
        "body": body,
        "excerpt": excerpt,
        "meta_description": meta_description,
        "keywords": keywords,
        "reading_time": reading_time,
        "word_count": word_count,
    }


# =============================================================================
# TOPIC SELECTION
# =============================================================================

CATEGORIES = [
    "APT Activity",
    "Ransomware", 
    "Vulnerability",
    "Supply Chain",
    "Threat Actor",
    "Industrial Control",
    "Cloud Security",
    "Defense",
]

TOPICS_BY_CATEGORY = {
    "APT Activity": [
        "Chinese APT Campaigns Targeting Critical Infrastructure",
        "Russian State Hackers and Their Latest Operations",
        "Iranian Cyber Espionage Tactics and Techniques",
        "North Korean APT Groups and Financial Theft",
        "APT Trends and What They Mean for Defenders",
        "Nation State Targeting of Defense Contractors",
        "Advanced Persistent Threats in the Healthcare Sector",
        "State Sponsored Attacks on Energy Infrastructure",
        "APT Lateral Movement Techniques Exposed",
        "Credential Harvesting by Nation State Actors",
        "APT Use of Living Off the Land Techniques",
        "Long Term Persistence Methods Used by APTs",
        "APT Targeting of Research and Academia",
        "State Actors Exploiting Zero Days",
        "APT Command and Control Infrastructure",
        "Espionage Campaigns Against Government Agencies",
        "APT Supply Chain Compromise Tactics",
        "Nation State Attacks on Financial Institutions",
        "APT Watering Hole Attack Campaigns",
        "Mobile Device Targeting by Nation States",
        "APT Use of Legitimate Cloud Services",
        "Diplomatic Targeting and Cyber Espionage",
        "APT Campaigns Against Telecommunications",
        "Space and Satellite System Targeting",
        "Election Infrastructure Threats",
        "Think Tank and NGO Targeting",
        "APT Exploitation of Trust Relationships",
        "Cyber Operations During Geopolitical Events",
        "APT Targeting of Vaccine Research",
        "Intellectual Property Theft Campaigns",
        "APT Prepositioning in Critical Systems",
        "Cyber Enabled Influence Operations",
        "APT Custom Malware Development",
        "Long Running Espionage Campaigns",
        "APT Targeting of Legal and Financial Advisors",
        "Aerospace Industry Targeting",
        "APT Evasion of Security Controls",
        "Cyber Proxy Operations",
        "APT Targeting of Journalists and Media",
        "Cyber Operations Against Dissidents",
        "APT Infrastructure Takedown Analysis",
        "State Actor Use of Criminal Tools",
        "APT Social Media Reconnaissance",
        "Supply Chain Espionage Operations",
        "APT Persistence Mechanism Analysis",
        "Counter Intelligence Cyber Operations",
        "APT Data Staging and Exfiltration",
        "Technology Sector Espionage Campaigns",
    ],
    "Ransomware": [
        "Ransomware Evolution and Current Trends",
        "Double Extortion Tactics in Modern Ransomware",
        "Ransomware Affiliate Programs and How They Work",
        "Healthcare Sector Ransomware Targeting",
        "Manufacturing Industry Under Ransomware Attack",
        "Ransomware Incident Response Best Practices",
        "Ransomware Prevention Strategies That Work",
        "The Business Model Behind Ransomware Operations",
        "Ransomware Encryption Techniques Analyzed",
        "Initial Access Brokers and Ransomware Gangs",
        "Ransomware Negotiation Tactics and Pitfalls",
        "Data Exfiltration Before Encryption",
        "Ransomware Targeting Backup Systems",
        "Education Sector Ransomware Attacks",
        "Municipal Government Ransomware Incidents",
        "Ransomware Rebranding and Group Evolution",
        "Cryptocurrency and Ransomware Payments",
        "Ransomware Recovery Without Paying",
        "Ransomware Attacks on Legal Services",
        "Retail Sector Ransomware Trends",
        "Ransomware Impact on Supply Chains",
        "Small Business Ransomware Survival Guide",
        "Ransomware and Cyber Insurance",
        "Post Ransomware Security Improvements",
        "Ransomware Playbook Analysis",
        "Weekend and Holiday Ransomware Attacks",
        "Ransomware Dwell Time Trends",
        "Cross Platform Ransomware Threats",
        "Ransomware Group Leadership Analysis",
        "Ransomware Code Reuse and Variants",
        "Ransomware Targeting of Backups",
        "Intermittent Encryption Techniques",
        "Ransomware and Data Destruction",
        "Human Operated Ransomware Tactics",
        "Ransomware Access Methods Analysis",
        "Ransomware Impact Assessment",
        "Law Enforcement Action on Ransomware",
        "Ransomware Victim Notification Strategies",
        "Ransomware Time to Encrypt Analysis",
        "Ransomware Operator Interviews",
        "Post Quantum Ransomware Concerns",
        "Ransomware and Industrial Systems",
        "Mobile Ransomware Threats",
        "Ransomware Decryptor Development",
        "Ransomware Victim Support Resources",
        "Ransomware Reporting Requirements",
        "Ransomware Tabletop Exercise Design",
        "Ransomware Recovery Timelines",
    ],
    "Vulnerability": [
        "Critical Vulnerabilities in Enterprise VPN Products",
        "Zero Day Exploits and Patch Prioritization",
        "Web Application Vulnerabilities That Matter",
        "Cloud Service Vulnerabilities and Misconfigurations",
        "Authentication Bypass Vulnerabilities",
        "Remote Code Execution Vulnerabilities Explained",
        "Vulnerability Management Program Best Practices",
        "When Patching Is Not Enough",
        "Memory Corruption Vulnerabilities Explained",
        "API Security Vulnerabilities in Modern Apps",
        "Deserialization Vulnerabilities and Exploits",
        "Privilege Escalation Vulnerabilities",
        "Firmware Vulnerabilities in Network Devices",
        "Browser Vulnerabilities and Exploit Chains",
        "Database Vulnerabilities and Data Exposure",
        "Email Server Vulnerabilities Under Attack",
        "Container Escape Vulnerabilities",
        "Vulnerability Chaining for Maximum Impact",
        "Active Directory Vulnerabilities",
        "Print Spooler Vulnerabilities Explained",
        "Exchange Server Security Flaws",
        "Log4j and Logging Library Risks",
        "SSL TLS Implementation Vulnerabilities",
        "IoT Device Vulnerability Landscape",
        "Virtual Infrastructure Vulnerabilities",
        "Collaboration Platform Security Flaws",
        "DNS Infrastructure Vulnerabilities",
        "Edge Device Vulnerability Trends",
        "UEFI and Firmware Vulnerabilities",
        "Bluetooth Vulnerability Landscape",
        "Wi-Fi Protocol Security Flaws",
        "Hardware Security Module Vulnerabilities",
        "Time Based Vulnerability Exploitation",
        "Race Condition Vulnerabilities",
        "Cryptographic Implementation Flaws",
        "OAuth and Authentication Vulnerabilities",
        "GraphQL Security Vulnerabilities",
        "Webhook Security Vulnerabilities",
        "Kernel Vulnerability Exploitation",
        "Hypervisor Escape Vulnerabilities",
        "PDF and Document Vulnerabilities",
        "Archive File Vulnerabilities",
        "Video Conferencing Vulnerabilities",
        "Instant Messaging Security Flaws",
        "Password Manager Vulnerabilities",
        "Antivirus Software Vulnerabilities",
        "Backup Software Security Flaws",
        "Version Control System Vulnerabilities",
    ],
    "Supply Chain": [
        "Software Supply Chain Attacks Explained",
        "Open Source Security Risks and Mitigations",
        "Third Party Risk Management Strategies",
        "SaaS Provider Security Considerations",
        "Hardware Supply Chain Concerns",
        "Managing Vendor Security Risk",
        "Supply Chain Attack Case Studies",
        "Building Supply Chain Resilience",
        "Code Signing Attacks and Defenses",
        "Dependency Confusion Attacks Explained",
        "Compromised Development Tools",
        "Supply Chain Attacks Through Updates",
        "Managed Service Provider Compromises",
        "Hardware Implants and Supply Chain Risk",
        "Software Bill of Materials Implementation",
        "Verifying Software Integrity at Scale",
        "Container Image Supply Chain Security",
        "Build Pipeline Security Best Practices",
        "CI CD Pipeline Compromise Risks",
        "Package Manager Security Concerns",
        "Source Code Repository Attacks",
        "Cloud Provider Supply Chain Risk",
        "Firmware Update Security",
        "Certificate Authority Compromise",
        "IDE and Developer Tool Risks",
        "Open Source Maintainer Compromise",
        "Supply Chain Visibility Challenges",
        "Vendor Assessment Best Practices",
        "Academic Software Supply Chain",
        "Gaming Industry Supply Chain Risks",
        "Financial Software Supply Chain",
        "Healthcare Software Dependencies",
        "Government Contractor Supply Chain",
        "Automotive Software Supply Chain",
        "Telecom Equipment Supply Chain",
        "Defense Industrial Base Supply Chain",
        "Retail Point of Sale Supply Chain",
        "Critical Infrastructure Vendor Risk",
        "AI Model Supply Chain Risks",
        "Data Pipeline Supply Chain Security",
        "SaaS Integration Security",
        "Plugin and Extension Security",
        "Theme and Template Security",
        "Font and Asset Supply Chain",
        "Analytics and Tracking Supply Chain",
        "CDN and Delivery Network Security",
        "DNS Provider Supply Chain Risk",
        "Certificate Lifecycle Management",
    ],
    "Threat Actor": [
        "Understanding Cybercriminal Motivation",
        "Threat Actor Profiling for Defenders",
        "Criminal Underground Marketplaces",
        "Insider Threat Detection and Prevention",
        "Hacktivism and Its Impact on Organizations",
        "The Relationship Between Crime and Nation States",
        "Threat Actor Tools and Infrastructure",
        "Attribution Challenges in Cyber Investigations",
        "Access Brokers in the Criminal Ecosystem",
        "Bulletproof Hosting and Criminal Infrastructure",
        "Threat Actor Recruitment and Operations",
        "Cybercrime as a Service Models",
        "Money Laundering in Cybercrime",
        "Threat Actor Communication Channels",
        "Criminal Collaboration and Competition",
        "Threat Intelligence Sources and Methods",
        "Tracking Threat Actor Evolution",
        "Disrupting Threat Actor Operations",
        "Ransomware Gang Profiles",
        "State Sponsored Hacker Groups",
        "Financially Motivated Threat Actors",
        "Script Kiddies to Sophisticated Actors",
        "Threat Actor Operational Security",
        "Criminal Forum Dynamics",
        "Threat Actor Target Selection",
        "Group Disbandment and Reformation",
        "Cross Border Criminal Cooperation",
        "Threat Actor Mistakes and Failures",
        "Threat Actor Use of AI Tools",
        "Social Engineering Specialist Groups",
        "Cryptomining Threat Actors",
        "Business Email Compromise Groups",
        "SIM Swapping Criminal Networks",
        "Data Broker Criminal Operations",
        "Threat Actor Brand Impersonation",
        "Credential Stuffing Operations",
        "Gift Card Fraud Networks",
        "Threat Actor Technical Training",
        "Threat Actor Infrastructure Patterns",
        "Criminal Specialization Trends",
        "Threat Actor Geographic Patterns",
        "Law Enforcement Impact on Actors",
        "Threat Actor Retirement Patterns",
        "Criminal Service Level Agreements",
        "Threat Actor Quality Assurance",
        "Underground Economy Pricing",
        "Threat Actor Dispute Resolution",
        "Criminal Reputation Systems",
    ],
    "Industrial Control": [
        "Industrial Control System Security Fundamentals",
        "OT Network Segmentation Strategies",
        "SCADA Security Challenges and Solutions",
        "IT OT Convergence Security Implications",
        "Critical Infrastructure Protection Priorities",
        "ICS Vulnerability Assessment Approaches",
        "Building an OT Security Program",
        "Legacy System Security in Industrial Environments",
        "PLC Security and Attack Vectors",
        "Industrial Protocol Security Weaknesses",
        "Remote Access to OT Environments",
        "ICS Incident Response Procedures",
        "Safety System Security Considerations",
        "Industrial IoT Security Challenges",
        "OT Asset Inventory and Visibility",
        "Engineering Workstation Security",
        "Industrial Network Monitoring Approaches",
        "Securing Industrial Wireless Networks",
        "Water Treatment Facility Security",
        "Power Grid Cybersecurity Challenges",
        "Oil and Gas Pipeline Security",
        "Manufacturing Execution System Security",
        "Building Automation System Risks",
        "Transportation System Cybersecurity",
        "Chemical Facility Security Requirements",
        "Nuclear Facility Cyber Protections",
        "Maritime and Port System Security",
        "Mining Operation Cybersecurity",
        "Food and Beverage Manufacturing Security",
        "Pharmaceutical Manufacturing Security",
        "Pulp and Paper Industry Security",
        "Steel and Metal Processing Security",
        "Semiconductor Fabrication Security",
        "Automotive Manufacturing Security",
        "Renewable Energy System Security",
        "Natural Gas Distribution Security",
        "Wastewater Treatment Security",
        "Airport Operations Technology Security",
        "Railway System Cybersecurity",
        "Aviation System Security",
        "Emergency Services Technology Security",
        "Smart City Infrastructure Security",
        "Agricultural Technology Security",
        "Logistics and Warehouse Automation",
        "Elevator and Escalator Control Security",
        "HVAC System Cybersecurity",
        "Fire and Life Safety System Security",
        "Physical Access Control Integration",
    ],
    "Cloud Security": [
        "Cloud Security Posture Management",
        "Identity and Access Management in the Cloud",
        "Container Security Best Practices",
        "Serverless Security Considerations",
        "Multi Cloud Security Challenges",
        "Cloud Data Protection Strategies",
        "Securing Cloud Native Applications",
        "Cloud Incident Response Procedures",
        "Cloud Misconfiguration Risks",
        "Kubernetes Security Fundamentals",
        "Cloud Privilege Escalation Attacks",
        "Securing Cloud Storage Services",
        "Cloud Network Security Controls",
        "Cloud Logging and Monitoring Strategy",
        "Secrets Management in Cloud Environments",
        "Cloud Workload Protection Platforms",
        "Securing Cloud Development Pipelines",
        "Cloud Compliance and Governance",
        "AWS Security Best Practices",
        "Azure Security Configuration Guide",
        "GCP Security Fundamentals",
        "Cloud Key Management Strategies",
        "Serverless Function Security",
        "Cloud Database Security",
        "Service Mesh Security Considerations",
        "Cloud Cost and Security Tradeoffs",
        "Cloud Forensics and Investigation",
        "Hybrid Cloud Security Architecture",
        "Cloud API Security Best Practices",
        "Cross Account Access Security",
        "Cloud Backup and Recovery Security",
        "Immutable Infrastructure Security",
        "Cloud Security Automation",
        "Multi Tenant Security Isolation",
        "Cloud Access Security Brokers",
        "Data Loss Prevention in Cloud",
        "Cloud Encryption Key Rotation",
        "Cloud Security Benchmarks",
        "Cloud Native Security Tools",
        "Policy as Code Implementation",
        "GitOps Security Practices",
        "Cloud Disaster Recovery Testing",
        "Cloud Vendor Lock In Mitigation",
        "Cloud Exit Strategy Planning",
        "Sovereign Cloud Considerations",
        "Edge Computing Security",
        "Cloud FinOps Security Integration",
        "Cloud Security Maturity Models",
    ],
    "Defense": [
        "Building a Threat Informed Defense",
        "Security Operations Center Best Practices",
        "Detection Engineering Fundamentals",
        "Incident Response Planning and Execution",
        "Threat Hunting Techniques That Work",
        "Security Architecture Principles",
        "Defense in Depth Implementation",
        "Measuring Security Program Effectiveness",
        "Purple Team Exercises for Better Defense",
        "Deception Technologies and Honeypots",
        "Endpoint Detection and Response Optimization",
        "Network Detection and Response Strategies",
        "Security Automation and Orchestration",
        "Tabletop Exercises for Incident Readiness",
        "Building a Security Champions Program",
        "Zero Trust Architecture Implementation",
        "Security Metrics That Matter",
        "Threat Intelligence Program Development",
        "Log Analysis for Threat Detection",
        "Memory Forensics Fundamentals",
        "Network Traffic Analysis Techniques",
        "Malware Analysis for Defenders",
        "Active Directory Security Hardening",
        "Email Security Gateway Optimization",
        "Web Application Firewall Tuning",
        "Vulnerability Scanning Best Practices",
        "Penetration Testing Program Management",
        "Red Team Blue Team Collaboration",
        "Behavioral Analytics for Security",
        "User Entity Behavior Analytics",
        "Data Loss Prevention Strategy",
        "Endpoint Hardening Best Practices",
        "Network Segmentation Implementation",
        "Application Allowlisting Deployment",
        "Security Awareness Training Programs",
        "Phishing Simulation Best Practices",
        "Incident Communication Planning",
        "Crisis Management for Security Teams",
        "Threat Modeling Methodologies",
        "Attack Surface Management",
        "Security Control Validation",
        "Continuous Security Monitoring",
        "Security Data Lake Architecture",
        "Alert Fatigue Reduction Strategies",
        "Security Tool Rationalization",
        "Managed Security Service Selection",
        "Security Budget Justification",
        "Building Security Team Culture",
    ],
}
def select_next_topic(state, force_category=None):
    """Select the next topic and category for content generation."""
    
    used_topics = state.get("used_topics", [])
    last_categories = state.get("last_categories", [])
    
    # Select category
    if force_category and force_category in CATEGORIES:
        category = force_category
    else:
        # Rotate through categories, avoiding recent ones
        available_categories = [c for c in CATEGORIES if c not in last_categories[-2:]]
        if not available_categories:
            available_categories = CATEGORIES
        category = random.choice(available_categories)
    
    # Select topic from category
    category_topics = TOPICS_BY_CATEGORY.get(category, TOPICS_BY_CATEGORY["Defense"])
    available_topics = [t for t in category_topics if t.lower() not in [u.lower() for u in used_topics[-20:]]]
    
    if not available_topics:
        available_topics = category_topics
    
    topic = random.choice(available_topics)
    
    # Update state
    if "last_categories" not in state:
        state["last_categories"] = []
    state["last_categories"].append(category)
    state["last_categories"] = state["last_categories"][-8:]
    
    return topic, category
