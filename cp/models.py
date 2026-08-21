from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# Create your models here.
class CPType(models.Model):   
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255,verbose_name='Наименование')
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name='Логотип'
    )
    icon = models.TextField(
            blank=True,
            null=True,
            verbose_name="SVG иконка",
        )
    
    
    class Meta:
        verbose_name = "Группа Котрагентов"
        verbose_name_plural = "Группы Котрагентов"

    def __str__(self): 
        return self.name
    
    @property
    def name_with_icon(self):
        if not self.icon:
            return self.name

        return format_html(

            '<div style="display:flex;align-items:center;gap:10px;">{}<span>{}</span></div>',
            mark_safe(self.icon),
            self.name,
        )
    

class CP(models.Model):
    id = models.CharField(max_length=255,primary_key=True)
    inn = models.CharField(max_length=25,verbose_name='ИНН')
    name = models.CharField(max_length=255,verbose_name='Наименование')
    cptype = models.ForeignKey(CPType,on_delete=models.DO_NOTHING,null=True,blank=True,verbose_name='Группа контрагентов')
    email = models.CharField(max_length=255,verbose_name='email',null=True,blank=True)
    ogrn = models.CharField(max_length=25,verbose_name='ОГРН',null=True,blank=True)
    phone = models.CharField(max_length=255,verbose_name='Телефон',null=True,blank=True)
    address = models.CharField(max_length=255,verbose_name='Адресс',null=True,blank=True)
    cp_work = models.CharField(max_length=100,verbose_name='Тип',null=True,blank=True)
    avatar = models.ImageField(
            upload_to="avatars/companies/",
            blank=True,
            null=True,
            verbose_name='Логотип'
        )
    icon = models.TextField(
            blank=True,
            null=True,
            verbose_name="SVG иконка",
        )

    class Meta:
        verbose_name = "Котрагент"
        verbose_name_plural = "Котрагенты"
        
    def __str__(self): 
        return self.name
    

