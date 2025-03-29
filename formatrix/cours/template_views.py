from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.views import View
from django.db import connection
from .models import Cours
from .forms import CoursForm
from django.shortcuts import render

class CoursListView(LoginRequiredMixin, ListView):
    model = Cours
    template_name = 'cours/cours_list.html'
    context_object_name = 'cours_list'
    login_url = '/login/'
    ordering = ['-created_at']  # Tri par défaut
    paginate_by = 10  # Nombre d'éléments par page

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Récupération des paramètres de l'API
        search = self.request.GET.get('search', '')
        ordering = self.request.GET.get('ordering', '-created_at')
        statut = self.request.GET.get('statut', '')
        type_cours = self.request.GET.get('type', '')
        
        # Application des filtres de l'API
        if search:
            queryset = queryset.filter(nom_cours__icontains=search)
            
        if statut:
            queryset = queryset.filter(statut_approbation=statut)
            
        if type_cours:
            queryset = queryset.filter(type_cours=type_cours)
            
        # Application du tri
        queryset = queryset.order_by(ordering)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Paramètres de l'API pour le template
        context.update({
            'search_query': self.request.GET.get('search', ''),
            'ordering': self.request.GET.get('ordering', '-created_at'),
            'statut_filter': self.request.GET.get('statut', ''),
            'type_filter': self.request.GET.get('type', ''),
            'show_create_button': True,
            'create_url': reverse_lazy('cours:cours-create'),
            'create_button_text': 'Créer un cours',
            'form_action': self.request.path,
            'reset_url': self.request.path,
            'has_active_filters': bool(
                self.request.GET.get('search', '') or 
                self.request.GET.get('statut', '') or 
                self.request.GET.get('type', '')
            )
        })
        return context

class CoursCreateView(LoginRequiredMixin, CreateView):
    model = Cours
    template_name = 'cours/cours_form.html'
    form_class = CoursForm
    success_url = reverse_lazy('cours:cours-list')
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch formateurs directly from the database to avoid ORM issues
        with connection.cursor() as cursor:
            cursor.execute("SELECT formateurid, nom, prenom FROM formateurs_formateur")
            formateurs = [
                {
                    'formateurid': row[0],
                    'nom': row[1],
                    'prenom': row[2]
                }
                for row in cursor.fetchall()
            ]
        context['formateurs'] = formateurs
        return context

    def form_valid(self, form):
        try:
            # Si le statut est 'approuve', on définit la date d'approbation
            if form.cleaned_data['statut_approbation'] == 'approuve':
                form.instance.date_approbation = timezone.now().date()
            
            # Save the form without the many-to-many field
            self.object = form.save(commit=False)
            self.object.save()
            
            # Handle the formateurs field manually using the correct table name
            formateur_ids = self.request.POST.getlist('formateurs')
            if formateur_ids:
                # First, clear any existing formateurs for this course
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM cours_formateurs WHERE cours_id = %s", [self.object.cours_id])
                
                # Then add the selected formateurs
                with connection.cursor() as cursor:
                    for formateur_id in formateur_ids:
                        cursor.execute(
                            "INSERT INTO cours_formateurs (cours_id, formateur_id) VALUES (%s, %s)",
                            [self.object.cours_id, formateur_id]
                        )
            
            messages.success(self.request, 'Le cours a été créé avec succès!')
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la création du cours: {str(e)}')
            return self.form_invalid(form)

class CoursDetailView(LoginRequiredMixin, DetailView):
    model = Cours
    template_name = 'cours/cours_detail.html'
    context_object_name = 'cours'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch formateurs for this course using the correct table name (cours_formateurs)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT f.formateurid, f.nom, f.prenom, f.type_formateur, f.niveau_expertise, f.specialites
                FROM formateurs_formateur f
                JOIN cours_formateurs cf ON f.formateurid = cf.formateur_id
                WHERE cf.cours_id = %s
            """, [self.object.cours_id])
            
            formateurs = []
            for row in cursor.fetchall():
                formateur = {
                    'formateurid': row[0],
                    'nom': row[1],
                    'prenom': row[2],
                    'type_formateur': row[3],
                    'niveau_expertise': row[4],
                    'specialites': row[5],
                    'get_full_name': f"{row[1]} {row[2]}",
                }
                
                # Add display values for type_formateur and niveau_expertise
                if row[3] == 'interne':
                    formateur['get_type_formateur_display'] = 'Interne'
                elif row[3] == 'externe':
                    formateur['get_type_formateur_display'] = 'Externe'
                elif row[3] == 'consultant':
                    formateur['get_type_formateur_display'] = 'Consultant'
                else:
                    formateur['get_type_formateur_display'] = row[3]
                    
                if row[4] == 'debutant':
                    formateur['get_niveau_expertise_display'] = 'Débutant'
                elif row[4] == 'intermediaire':
                    formateur['get_niveau_expertise_display'] = 'Intermédiaire'
                elif row[4] == 'expert':
                    formateur['get_niveau_expertise_display'] = 'Expert'
                else:
                    formateur['get_niveau_expertise_display'] = row[4]
                
                formateurs.append(formateur)
        
        context['course_formateurs'] = formateurs
        return context

class CoursUpdateView(LoginRequiredMixin, View):
    template_name = 'cours/cours_form.html'
    login_url = '/login/'
    
    def get(self, request, pk):
        # Fetch the course directly from the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cours_id, nom_cours, description, niveau, frais_par_participant,
                       duree_heures, periode_mois, type_cours, objectifs, prerequis,
                       materiel_requis, horaire, statut_approbation, date_approbation,
                       date_expiration_validite, version, start_time
                FROM cours
                WHERE cours_id = %s
            """, [pk])
            
            row = cursor.fetchone()
            if not row:
                raise Http404("Course not found")
            
            # Create a Cours object with the fetched data
            course = Cours(
                cours_id=row[0],
                nom_cours=row[1],
                description=row[2],
                niveau=row[3],
                frais_par_participant=row[4],
                duree_heures=row[5],
                periode_mois=row[6],
                type_cours=row[7],
                objectifs=row[8],
                prerequis=row[9],
                materiel_requis=row[10],
                horaire=row[11],
                statut_approbation=row[12],
                date_approbation=row[13],
                date_expiration_validite=row[14],
                version=row[15],
                start_time=row[16]
            )
        
        # Create a form with the course data
        form = CoursForm(instance=course)
        
        # Fetch formateurs directly from the database
        with connection.cursor() as cursor:
            cursor.execute("SELECT formateurid, nom, prenom FROM formateurs_formateur")
            formateurs = [
                {
                    'formateurid': row[0],
                    'nom': row[1],
                    'prenom': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        # Get the currently selected formateurs for this course
        with connection.cursor() as cursor:
            cursor.execute("SELECT formateur_id FROM cours_formateurs WHERE cours_id = %s", [pk])
            selected_formateur_ids = [row[0] for row in cursor.fetchall()]
            
        # Mark which formateurs are selected
        for formateur in formateurs:
            formateur['selected'] = formateur['formateurid'] in selected_formateur_ids
        
        # Render the template with the form and context
        return render(request, self.template_name, {
            'form': form,
            'formateurs': formateurs,
            'object': course
        })
    
    def post(self, request, pk):
        # Fetch the course directly from the database
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cours_id, nom_cours, description, niveau, frais_par_participant,
                       duree_heures, periode_mois, type_cours, objectifs, prerequis,
                       materiel_requis, horaire, statut_approbation, date_approbation,
                       date_expiration_validite, version, start_time
                FROM cours
                WHERE cours_id = %s
            """, [pk])
            
            row = cursor.fetchone()
            if not row:
                raise Http404("Course not found")
            
            # Create a Cours object with the fetched data
            course = Cours(
                cours_id=row[0],
                nom_cours=row[1],
                description=row[2],
                niveau=row[3],
                frais_par_participant=row[4],
                duree_heures=row[5],
                periode_mois=row[6],
                type_cours=row[7],
                objectifs=row[8],
                prerequis=row[9],
                materiel_requis=row[10],
                horaire=row[11],
                statut_approbation=row[12],
                date_approbation=row[13],
                date_expiration_validite=row[14],
                version=row[15],
                start_time=row[16]
            )
        
        # Create a form with the POST data and the course instance
        form = CoursForm(request.POST, instance=course)
        
        if form.is_valid():
            try:
                # Extract form data
                data = form.cleaned_data
                
                # Set date_approbation if status is 'approuve'
                date_approbation = None
                if data['statut_approbation'] == 'approuve':
                    date_approbation = timezone.now().date()
                    
                    # Calculate expiration date (1 year from approval)
                    date_expiration = date_approbation + timezone.timedelta(days=365)
                else:
                    date_expiration = None
                
                # Update the course directly in the database using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE cours
                        SET nom_cours = %s, description = %s, niveau = %s, 
                            frais_par_participant = %s, duree_heures = %s, 
                            periode_mois = %s, type_cours = %s, objectifs = %s, 
                            prerequis = %s, materiel_requis = %s, horaire = %s, 
                            statut_approbation = %s, date_approbation = %s,
                            date_expiration_validite = %s, start_time = %s
                        WHERE cours_id = %s
                    """, [
                        data['nom_cours'], data['description'], data['niveau'],
                        data['frais_par_participant'], data['duree_heures'],
                        data['periode_mois'], data['type_cours'], data['objectifs'],
                        data['prerequis'], data['materiel_requis'], data['horaire'],
                        data['statut_approbation'], date_approbation,
                        date_expiration, data['start_time'], pk
                    ])
                
                # Handle the formateurs field manually
                formateur_ids = request.POST.getlist('formateurs')
                
                # First, clear any existing formateurs for this course
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM cours_formateurs WHERE cours_id = %s", [pk])
                
                # Then add the selected formateurs
                if formateur_ids:
                    with connection.cursor() as cursor:
                        for formateur_id in formateur_ids:
                            cursor.execute(
                                "INSERT INTO cours_formateurs (cours_id, formateur_id) VALUES (%s, %s)",
                                [pk, formateur_id]
                            )
                
                messages.success(request, 'Le cours a été mis à jour avec succès!')
                return redirect('cours:cours-list')
            except Exception as e:
                messages.error(request, f'Erreur lors de la mise à jour du cours: {str(e)}')
        else:
            # If the form is invalid, display the errors
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
        
        # Fetch formateurs again for the form
        with connection.cursor() as cursor:
            cursor.execute("SELECT formateurid, nom, prenom FROM formateurs_formateur")
            formateurs = [
                {
                    'formateurid': row[0],
                    'nom': row[1],
                    'prenom': row[2]
                }
                for row in cursor.fetchall()
            ]
            
        # Get the currently selected formateurs for this course
        with connection.cursor() as cursor:
            cursor.execute("SELECT formateur_id FROM cours_formateurs WHERE cours_id = %s", [pk])
            selected_formateur_ids = [row[0] for row in cursor.fetchall()]
            
        # Mark which formateurs are selected
        for formateur in formateurs:
            formateur['selected'] = formateur['formateurid'] in selected_formateur_ids
        
        # Render the template with the form and context
        return render(request, self.template_name, {
            'form': form,
            'formateurs': formateurs,
            'object': course
        })

class CoursDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cours
    template_name = 'cours/cours_confirm_delete.html'
    success_url = reverse_lazy('cours:cours-list')
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent supprimer un cours
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        cours = self.get_object()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été supprimé avec succès!')
        return super().delete(request, *args, **kwargs)

class CoursApprouverView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent approuver un cours
        return self.request.user.is_staff
    
    def get(self, request, pk):
        cours = get_object_or_404(Cours, pk=pk)
        cours.statut_approbation = 'approuve'
        cours.date_approbation = timezone.now().date()
        # La date d'expiration sera automatiquement calculée dans la méthode save() du modèle
        cours.save()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été approuvé avec succès!')
        return HttpResponseRedirect(reverse_lazy('cours:cours-list'))

class CoursRefuserView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/login/'
    
    def test_func(self):
        # Seuls les administrateurs peuvent refuser un cours
        return self.request.user.is_staff
    
    def get(self, request, pk):
        cours = get_object_or_404(Cours, pk=pk)
        cours.statut_approbation = 'refuse'
        cours.date_approbation = None
        cours.date_expiration_validite = None
        cours.save()
        messages.success(request, f'Le cours "{cours.nom_cours}" a été refusé!')
        return HttpResponseRedirect(reverse_lazy('cours:cours-list'))
