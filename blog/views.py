from django.shortcuts import render, get_object_or_404, redirect
from .forms import MoveForm
from .models import Animal, Equipement


def animal_list(request):
    animals = Animal.objects.filter()	
    equipements = Equipement.objects.order_by('id_equip')
    return render(request, 'animalerie/animal_list.html', {'animals': animals, 'equipements': equipements})

def animal_detail(request, id_animal):
    message = ''
    error = None
    animal = get_object_or_404(Animal, id_animal=id_animal)
    form = MoveForm(request.POST, instance=animal)
    ancien_lieu = get_object_or_404(Equipement, id_equip=animal.lieu.id_equip)
    if request.method == 'POST' and form.is_valid():
        form.save(commit=False)
        nouveau_lieu = get_object_or_404(Equipement, id_equip=animal.lieu.id_equip)
        if nouveau_lieu.disponibilite == 'libre' and check_etats(animal, nouveau_lieu.id_equip):
            ancien_lieu.disponibilite = "libre"
            ancien_lieu.save()
            refresh_etats(animal, nouveau_lieu.id_equip)
            form.save()
            if nouveau_lieu.id_equip == 'Litière':  # Pour que les litière restent toujours libre
                nouveau_lieu.disponibilite = "libre"
            else:
                nouveau_lieu.disponibilite = "occupé"
            nouveau_lieu.save()
            message = f'{animal.id_animal} est maintenant à {nouveau_lieu.id_equip} et il/elle est {animal.etat}.'
            error = False
        else:
            message = 'Cette modification ne peut pas être realisée.'
            error = True

        return render(request, 'animalerie/animal_detail.html', {'animal': animal, 'lieu': ancien_lieu, 'form': form, 'message': message, 'error': error})

    else:
        form = MoveForm()
        return render(request, 'animalerie/animal_detail.html', {'animal': animal, 'lieu': ancien_lieu, 'form': form, 'message': message, 'error': error})


# Fonction qui renvoie "True" si le nouvel lieu est correctement lié à son état
def check_etats (animal, n_lieu):
    if n_lieu == 'Litière' and animal.etat == 'endormi':
        return True
    elif n_lieu == 'Mangeoire' and animal.etat == 'affamé':
        return True
    elif n_lieu == 'Roue' and animal.etat == 'repus':
        return True
    elif n_lieu == 'Nid' and animal.etat == 'fatigué':
        return True
    else:
        return False

# Fonction qui met à jour l'état de l'animal en fonction de sa lieu
def refresh_etats (animal,lieu):
    if lieu == 'Litière':
        animal.etat = 'affamé'
    elif lieu == 'Mangeoire':
        animal.etat = 'repus'
    elif lieu == 'Roue':
        animal.etat = 'fatigué'
    elif lieu == 'Nid':
        animal.etat = 'endormi'
    animal.save()
    pass