import sys
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from config import Config
from app.models import *
from app import app, db

socketio = SocketIO(app)

#index route
@app.route('/')
def index():
    workspaces = Workspace.query.all()
    return render_template('createWorkspace.html',workspaces = workspaces)

#create workspace. form is in index route
@app.route("/add_workspace/", methods=["POST"])
def add_workspace():
    if request.method =="POST":
        workspaceName = request.form.get("workspaceName")
        newWorkspace = Workspace(workspaceName = workspaceName)
        db.session.add(newWorkspace)
        db.session.commit()
        newWorkspace.addsubgroup("General")
        return redirect(url_for('workspace', workspaceId=newWorkspace.id))

#workspace route / create subgroups
@app.route("/<int:workspaceId>", methods=["GET", "POST"])
def workspace(workspaceId):
    workspace = Workspace.query.get(workspaceId)
    subgroups = workspace.subgroups
    if request.method =="POST":
        subgroupName = request.form.get("subgroupName")
        workspace.addsubgroup(subgroupName)
        return redirect(url_for('workspace', workspaceId=workspaceId))
    return render_template('workspace.html', subgroups = subgroups, workspace = workspace)


#subgroups route and messages
@app.route("/<int:workspaceId>/<int:subgroupId>", methods=["GET"])#CHANGE ONLY TO GET
def subgroup(workspaceId, subgroupId):
    workspace = Workspace.query.get(workspaceId)
    subgroup = subGroup.query.get(subgroupId)
    messages = subgroup.messages
    return render_template('subgroup.html', workspace=workspace, subgroup=subgroup, messages=messages)

@app.route("/<int:workspaceId>/<int:subgroupId>/messages", methods=["POST"])#FIGURE OUT WAY TO GET TTHIS ROUTE TO SHOW UP IN SUBGROUP ROUTE
def message(workspaceId, subgroupId):
    workspace = Workspace.query.get(workspaceId)
    subgroup = subGroup.query.get(subgroupId)
    messages = subgroup.messages
    subgroup.addMessage(message)
    return render_template('subgroup.html',workspace=workspace,subgroup=subgroup,messages=messages)


@socketio.on('message')
def handleMessage(msg,workspaceId, subgroupId):
    print('message: ' +msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
	socketio.run(app)
