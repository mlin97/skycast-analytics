import os
import tarfile
import time
from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1
from google.cloud import run_v2

def create_archive(source_dir, output_filename):
    """Zips the source directory into a tar.gz file."""
    print(f"📦 Zipping source code from {source_dir}...")
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    print(f"✅ Created archive: {output_filename}")

def upload_to_gcs(bucket_name, source_file, destination_blob_name):
    """Uploads a file to the bucket."""
    print(f"☁️  Uploading to gs://{bucket_name}/{destination_blob_name}...")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"✅ Upload successful.")
    return f"gs://{bucket_name}/{destination_blob_name}"

def build_image(project_id, source_uri, image_name):
    """Triggers Cloud Build to build the container image."""
    print(f"🔨 Triggering Cloud Build for {image_name}...")
    client = cloudbuild_v1.CloudBuildClient()
    
    build = cloudbuild_v1.Build()
    # Cloud Build expects source in GCS
    build.source = cloudbuild_v1.Source(
        storage_source=cloudbuild_v1.StorageSource(
            bucket=source_uri.split("/")[2],
            object_= "/".join(source_uri.split("/")[3:])
        )
    )
    
    # Simple build step using Docker
    # Note: Using Kaniko or just 'gcr.io/cloud-builders/docker' is standard
    step = cloudbuild_v1.BuildStep(
        name="gcr.io/cloud-builders/docker",
        args=["build", "-t", image_name, "."]
    )
    build.steps = [step]
    
    # Push the image to registry
    build.images = [image_name]
    
    operation = client.create_build(project_id=project_id, build=build)
    print(f"⏳ Build in progress... (Operation: {operation.metadata.build.id})")
    
    # Wait for result
    result = operation.result()
    print(f"✅ Build complete. Image: {image_name}")
    return image_name

def deploy_service(project_id, image_name, service_name, region="us-central1"):
    """Deploys the image to Cloud Run."""
    print(f"🚀 Deploying service {service_name} to Cloud Run in {region}...")
    client = run_v2.ServicesClient()
    
    parent = f"projects/{project_id}/locations/{region}"
    service_id = f"projects/{project_id}/locations/{region}/services/{service_name}"
    
    # Define the service
    container = run_v2.Container(
        image=image_name,
        ports=[run_v2.ContainerPort(container_port=8501)]
    )
    
    template = run_v2.RevisionTemplate(
        containers=[container]
    )
    
    service = run_v2.Service(
        template=template
    )
    
    # Check if service exists (to update) or create new
    request = run_v2.UpdateServiceRequest(
        service=service
    )
    # We need to set the name for Update
    service.name = service_id
    
    try:
        # Try updating first
        operation = client.update_service(request=request)
        print("⏳ Update in progress...")
    except Exception:
        print("ℹ️  Service not found, creating new service...")
        request = run_v2.CreateServiceRequest(
            parent=parent,
            service=service,
            service_id=service_name
        )
        operation = client.create_service(request=request)
        print("⏳ Creation in progress...")
        
    response = operation.result()
    print(f"✅ Deployment successful!")
    print(f"🌍 Service URL: {response.uri}")

if __name__ == "__main__":
    # Configuration
    PROJECT_ID = "my-vibe-app-skycast-99"
    BUCKET_NAME = "my-vibe-app-skycast-99-bucket"
    APP_NAME = "skycast-analytics"
    IMAGE_URI = f"gcr.io/{PROJECT_ID}/{APP_NAME}:latest"
    
    if not PROJECT_ID or not BUCKET_NAME:
        print("❌ Project ID and Bucket Name are required.")
        exit(1)
        
    try:
        # 1. Zip
        archive_name = "source.tar.gz"
        create_archive(".", archive_name)
        
        # 2. Upload
        source_gcs_uri = upload_to_gcs(BUCKET_NAME, archive_name, f"source/{int(time.time())}_source.tar.gz")
        
        # 3. Build
        build_image(PROJECT_ID, source_gcs_uri, IMAGE_URI)
        
        # 4. Deploy
        deploy_service(PROJECT_ID, IMAGE_URI, APP_NAME)
        
        # Cleanup
        if os.path.exists(archive_name):
            os.remove(archive_name)
            
    except Exception as e:
        print(f"❌ Error: {e}")
