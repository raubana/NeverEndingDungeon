
def lerp(a,b,p):
	return a+(b-a)*p

def invlerp(a,b,c):
    return (c-a)/(b-a)

def lerp_pos(a,b,p):
	return [lerp(a[0],b[0],p),lerp(a[1],b[1],p)]

def lerp_colors(a,b,p):
	return [int(lerp(a[0],b[0],p)),int(lerp(a[1],b[1],p)),int(lerp(a[2],b[2],p))]

def copy_color(a):
	return (int(a[0]),int(a[1]),int(a[2]))

def bezier(points, p):
    if len(points) == 1:
        return points[0]
    new_points = []
    i = 0
    while i < len(points)-1:
        new_points.append(lerp_pos(points[i], points[i+1], p))
        i += 1
    return bezier(new_points,p)


