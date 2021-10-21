import vpython as vs
import _thread


def vthread():
    print("coucou")
    vs.scene.title = "Sphere in space (3D drag with right mouse button)"
    vs.scene.autoscale = False
    sphere = vs.sphere(pos=vs.vector(0, 0, 0), color=vs.color.green)
    return 0


global sphere


th = _thread.start_new_thread(vthread, ())
