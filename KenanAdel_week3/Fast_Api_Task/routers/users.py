from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import models.user as models
import models.project as project_models
import schemas.user as schemas
from database import get_db
from auth import get_password_hash, verify_password, create_access_token, get_current_user


router = APIRouter(prefix="/users", tags=["Users"])

# start Create_User
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already used")

    hashed_pwd = get_password_hash(user.password)
    
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
# end Create_User


# start Login_User
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
# end Login_User


#start Read_All_Users 
@router.get("/", response_model=List[schemas.UserResponse])
def read_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.User).all()
#end Read_All_Users 


# start Read_Single_User
@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
# end Read_Single_User


#start Update_User
@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user
#end Update_User


#start Delete_User
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_projects = db.query(project_models.Project).filter(project_models.Project.owner_id == user_id).first()
    if user_projects:
        raise HTTPException(status_code=400, detail="Cannot delete user: They own one or more projects Please reassign or delete their projects first")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
#end Delete_User
