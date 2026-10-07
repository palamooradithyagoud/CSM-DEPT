from datetime import datetime
import uuid
from app.extensions import db


class DepartmentInfo(db.Model):
    """Core public department identity and leadership details."""
    __tablename__ = "department_info"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False, default="Department of Computer Science & Engineering")
    short_code = db.Column(db.String(20), nullable=False, default="CSE")
    tagline = db.Column(db.String(255), default="Empowering Future Innovators & Academic Excellence")
    about = db.Column(db.Text, nullable=False)
    vision = db.Column(db.Text, nullable=False)
    mission = db.Column(db.Text, nullable=False)
    hod_name = db.Column(db.String(120), nullable=False, default="Dr. M. A. Jabbar")
    hod_designation = db.Column(db.String(120), default="Professor & Head of Department")
    hod_qualification = db.Column(db.String(120), default="Ph.D. (CSE), M.Tech, B.Tech, SMIEEE")
    hod_message = db.Column(db.Text, nullable=False)
    hod_photo_url = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), default="hod.cse@college.edu")
    contact_phone = db.Column(db.String(50), default="+91 40 2345 6789")
    office_location = db.Column(db.String(150), default="Block-A, Room 302, Academic Enclave")
    established_year = db.Column(db.Integer, default=2008)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "shortCode": self.short_code,
            "tagline": self.tagline,
            "about": self.about,
            "vision": self.vision,
            "mission": self.mission,
            "hod": {
                "name": self.hod_name,
                "designation": self.hod_designation,
                "qualification": self.hod_qualification,
                "message": self.hod_message,
                "photoUrl": self.hod_photo_url,
            },
            "contact": {
                "email": self.contact_email,
                "phone": self.contact_phone,
                "officeLocation": self.office_location,
            },
            "establishedYear": self.established_year,
        }


class FacultyMember(db.Model):
    """Department faculty profiles."""
    __tablename__ = "faculty_members"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(120), nullable=False)  # Professor, Associate Professor, Assistant Professor
    qualification = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    experience_years = db.Column(db.Integer, default=5)
    bio = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "designation": self.designation,
            "qualification": self.qualification,
            "specialization": self.specialization,
            "email": self.email,
            "phone": self.phone,
            "experienceYears": self.experience_years,
            "bio": self.bio,
            "photoUrl": self.photo_url,
            "displayOrder": self.display_order,
        }


class DepartmentEvent(db.Model):
    """Public department events, workshops, conferences, and symposiums."""
    __tablename__ = "department_events"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Workshop, Hackathon, Conference, Guest Lecture, Cultural
    event_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_upcoming = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "eventDate": self.event_date.isoformat() if self.event_date else None,
            "location": self.location,
            "imageUrl": self.image_url,
            "isFeatured": self.is_featured,
            "isUpcoming": self.is_upcoming,
        }


class StudentAchievement(db.Model):
    """Showcase of student achievements (Hackathons, Patents, Research, Placements)."""
    __tablename__ = "student_achievements"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    student_names = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Hackathon, Research Publication, Competitive Programming, Innovation
    event_name = db.Column(db.String(200), nullable=False)
    award = db.Column(db.String(120), nullable=False)  # 1st Prize, Finalist, Gold Medal
    achievement_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "studentNames": self.student_names,
            "category": self.category,
            "eventName": self.event_name,
            "award": self.award,
            "date": self.achievement_date.isoformat() if self.achievement_date else None,
            "description": self.description,
            "imageUrl": self.image_url,
        }


class Announcement(db.Model):
    """Department notices, examination schedules, and official circulars."""
    __tablename__ = "announcements"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default="Circular")  # Circular, Examination, Academic, Placement
    is_pinned = db.Column(db.Boolean, default=False)
    publish_date = db.Column(db.Date, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "isPinned": self.is_pinned,
            "publishDate": self.publish_date.isoformat() if self.publish_date else None,
        }
