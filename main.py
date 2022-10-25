from flask import Flask,request,jsonify,session,redirect,url_for,render_template
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict,defaultdict

app=Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Buildings.sqlite3'
db = SQLAlchemy(app)

class Buildings(db.Model):
	__tablename__ = "Buildings"

	_id = db.Column("id",db.Integer,primary_key=True)
	building_name = db.Column(db.String(100),unique=True,nullable=False)
	desks = db.Column(db.Integer,nullable=False)
	floors = db.Column(db.Integer,nullable=False)
	_taken = db.Column(db.String,nullable=True)
	_desks_perfloor = db.Column(db.String,nullable=True)
	

	def __init__(self,building_name,desks,floors,_taken,_desks_perfloor):
		self.building_name = building_name
		self.desks = desks
		self.floors = floors
		self._taken = _taken
		self._desks_perfloor= _desks_perfloor
		

	@property
	def desks_perfloor(self):
		return [float(x) for x in self._desks_perfloor.split(';')]

	@desks_perfloor.setter
	def desks_perfloor(self,value):
		self._desks_perfloor+=';%s' % value
	

	@property
	def taken_index(self):
		return [float(x) for x in self._taken.split(';')]

	@taken_index.setter
	def taken_index(self,value):
		self._taken =  value

	@property
	def taken(self):
		return [float(x) for x in self._taken.split(';')]




	@taken.setter
	def taken(self,value):
		self._taken+=';%s' % value


	@property
	def serialize(self):
		return {
			'building_name': self.building_name,
			'floors': self.floors,
			'desks': self.desks,
			'taken': self.taken,
			'id': self._id,
		}



'''total_buildings = [
	{
		'id':1,
		'title':'Building 1'
	},
	{
		'id':2,
		'title':'Building 2'
	}
]'''



def update_building(id,building_name,total_floors,total_desks,taken):
	updated_building = Buildings.query.filter_by(_id=id).one()
	if not taken:
		updated_building.taken = taken

	db.session.add(updated_building)
	db.session.commit()


@app.route("/buildings/add",methods=['GET','POST'])
def add_building():
	print("here")
	print(request.method)
	if request.method == "POST":
		#building_name = request.args.get('building_name', 'building 1')
		building_name = request.form["building_name"]
		#total_floors = request.args.get('total_floors', '20')
		total_floors = request.form["floors"]
		#total_desks = request.args.get('total_desks', '100')
		total_desks = request.form["desks"]
		taken = request.args.get('taken', '0')
		desks_perfloor = request.args.get('_desks_perfloor', '0')
		add_building = Buildings(building_name=building_name,floors=total_floors ,desks=total_desks,_taken=taken,_desks_perfloor=desks_perfloor)
		db.session.add(add_building)
		db.session.commit()
		single_building = Buildings.query.filter_by(building_name=building_name).one()
		for i in range(0,single_building.floors):
			single_building.taken=0
		print (single_building.taken)
		db.session.add(single_building)
		db.session.commit()
		
		return redirect(url_for('add_desks',building_name=building_name))
	else:
		return render_template("addbuilding.html")
	#return add_newbuilding(building_name,total_floors,total_desks,taken)




@app.route("/add_desks/<building_name>",methods=["GET","POST"])
def add_desks(building_name=None):
	print(building_name)
	if request.method == "GET":
		return render_template("addDesks.html",val=Buildings.query.filter_by(building_name=building_name))
	else:
		adding_floor = Buildings.query.filter_by(building_name=building_name).one()
		print(adding_floor.floors)
		for i in range(0,adding_floor.floors):
			k = str(i)
			floor = request.form[k]
			adding_floor.desks_perfloor=floor

		db.session.add(adding_floor)
		db.session.commit()
		return redirect(url_for('getallbuilding'))





@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/buildings/all",methods=['GET'])
def getallbuilding():
	c = Buildings.query.count()
	if c!=0:
		return render_template("buildings.html",values = Buildings.query.all())
	else:
		return render_template("home.html")


@app.route("/buildings/select_floor",methods=['GET','POST'])
def get_perticular_building():
	total_buildings = Buildings.query.all()
	#print (request.args['id'])
	#print(id)
	print(request.method)
	if 'id' in request.args:
		id = int(request.args['id'])
	else:
		return "Error, no such id"

	if request.method == "GET":
		return render_template("inside.html",values = Buildings.query.filter_by(_id=id))
	else:
		for building in total_buildings:
			if building._id == id:
				updated_building = Buildings.query.filter_by(_id=id).one()
				index = request.form['options']
				print(index,'=',updated_building.taken[int(index)])
				update_floor = updated_building.taken[int(index)]
				res=[]
				res=list(updated_building.taken)
				updated_building.taken_index='0.0'
				print (res)
				for i in range(0,updated_building.floors+1):
					if i == int(index):
						res[i] = res[i] + 1
					elif res[i]==0:
						res[i] = 0.0

					print(res)
					if i>0:
						updated_building.taken = res[i]		


				print (updated_building.taken)
				db.session.add(updated_building)
				db.session.commit()
				
		return redirect(url_for('getallbuilding'))


if __name__ == "__main__":
	db.create_all()
	app.run()
