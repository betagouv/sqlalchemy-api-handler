class Check():

    def find_or_create(self, **props):
        existing = self.query.filter_by(**props).first()
        if existing:
            return existing
        new = self()
        for key, value in props.items():
            setattr(new, key, value)
        return new


    def find_and_update(self, content):

        content = {
            'description': 'blabla',
            'entity': 'breitbart',
            'label': 'blabla'
        }


        # je trouve ttes les column primary keys dans mon content

        primary_keys_content = {
            entity: 'breitbart'
            #'id': 'AE',
        }




    create_or_find() => cherche un truc qui  .... on le save



    ApiHandler.save(organisation, organisation2, organisation3)








        existing = self.query.filter_by(**props).first()


















@app('/organization')
def create_or_modify_organization():

    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: blabla
    organization = organization.find__update() #id AE, entity: 'breitbart', label: 'foo'
    #organization = organization.populate_from_dict(request.json) # id AE, label: blabla
    ApiHandler.save(organization)



    find
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.find() #id AE, entity: 'breitbart', label: 'OLD LABEL'





    find_or_create (ca existe pas deja)
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.find_or_create() #id unsaved, entity: 'breitbart', label: 'NEW LABEL'

    find_or_create (ca existe deja)
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.find_or_create() #id AE, entity: 'breitbart', label: 'OLD LABEL'






    find_and_update (ca existe pas deja)
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.find_and_update() # ERROR

    find_and_update (ca existe deja)
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.find_and_update() #id AE, entity: 'breitbart', label: 'OLD LABEL'




    create_or_update ca existe pas deja
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.create_or_update() # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'

    ca existe deja
    organization = Organization(request.json) # id: unsaved, entity: 'breitbart', label: 'NEW LABEL'
    organization = organization.create_or_update() # id: AE, entity: 'breitbart', label: 'NEW LABEL'









find_or_create
find_and_update
