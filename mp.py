from multiprocessing import Process, Pipe
from time import sleep



# plt.yticks(range(1,1000))
def graph(pipe):
    import matplotlib.pyplot as plt
    import numpy as np

    def setup_backend(backend='TkAgg'):
        import sys
        del sys.modules['matplotlib.backends']
        del sys.modules['matplotlib.pyplot']
        import matplotlib as mpl
        mpl.use(backend)  # do this before importing pyplot
        import matplotlib.pyplot as plt
        return plt

    def animate():
        print "kur"
        N = 8
        # rects = plt.bar(range(N), range(0,8), align='center')

        while True:
            data = pipe.recv()
            print data
            plt.plot(data, data, 'bo')
            # for i in range(8):
                # for rect, h in zip(rects, data):
                    # rect.set_height(float(h))
            fig.canvas.draw()

    plt = setup_backend()
    fig = plt.figure()
    plt.autoscale(enable=True, axis='both', tight=None)
    win = fig.canvas.manager.window
    win.after(1000, animate)
    plt.show()


# graph(None)
pipe, child = Pipe()
p = Process(target=graph, args=(child,))
p.start()
data = [1]
for i in range(100):
    data.append(i)
    pipe.send(data)
    # sleep(0.2)