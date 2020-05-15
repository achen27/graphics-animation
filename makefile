test: face.mdl robot.mdl simple_anim.mdl main.py matrix.py mdl.py display.py draw.py gmath.py
	# python main.py face.mdl
	# python3 main.py robot.mdl
	python main.py simple_anim.mdl

clean:
	rm *pyc *out parsetab.py

clear:
	rm *pyc *out parsetab.py *ppm
