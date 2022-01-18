# Machining Assistant
This is a machining calculator, reporting Fusion360 parameters and g-code, estimating performance, and offering suggestions for the selected machine. The web interface is supported by a units-aware Python machining analytics module [pymachining](https://github.com/kentavv/pymachining). I intended to continue developing this to teach machining theory and incorperate emperical models. However, today the reports are built on published equations and tables. 

Useful or unique elements of this work include:
1) The Fusion360 parameters are shown with marked up Fusion360 dialogs.
2) Usable g-code is generated with the calculated parameters built-in.
3) Alterantives are generated and sortable along dimensions of machine capacity.

By publishing this work, I hope that any useful ideas can be incorperated into the work of others.

A live example can be found [here](https://confluencerd.com/apps/machining_assistant/assistant.fcgi).
