from django.core.management.base import BaseCommand
from customer.models import KYCform, CopyOfOmang, ResidenceProof, IncomeProof, HomeownersCover, ThirdPartyCarInsurance


class Command(BaseCommand):
    help = 'Clean up old Google Cloud Storage URLs from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        models_to_clean = [
            (KYCform, 'kyc_form'),
            (CopyOfOmang, 'copy_of_omang'),
            (ResidenceProof, 'residence_proof'),
            (IncomeProof, 'income_proof'),
            (HomeownersCover, 'title_deed'),
            (ThirdPartyCarInsurance, 'blue_book'),
        ]
        
        total_cleaned = 0
        
        for model_class, field_name in models_to_clean:
            self.stdout.write(f'\nChecking {model_class.__name__} model...')
            
            # Find records with Google Cloud Storage URLs
            gcs_records = model_class.objects.filter(
                **{f'{field_name}__icontains': 'storage.googleapis.com'}
            )
            
            count = gcs_records.count()
            if count > 0:
                self.stdout.write(f'Found {count} records with Google Cloud Storage URLs')
                
                for record in gcs_records:
                    field_value = getattr(record, field_name)
                    if field_value and 'storage.googleapis.com' in str(field_value):
                        self.stdout.write(f'  - {record.customer.user.username}: {field_value}')
                        
                        if not dry_run:
                            # Clear the field value to remove the broken URL
                            setattr(record, field_name, '')
                            record.save()
                            self.stdout.write(f'    ✓ Cleared broken URL')
                        else:
                            self.stdout.write(f'    → Would clear this URL')
                
                total_cleaned += count
            else:
                self.stdout.write('  No Google Cloud Storage URLs found')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDry run complete. Would clean {total_cleaned} records.'))
            self.stdout.write('Run without --dry-run to actually clean the database.')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nCleaned {total_cleaned} records with old Google Cloud Storage URLs.'))
            self.stdout.write('Users will need to re-upload their documents.')