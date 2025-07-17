#!/usr/bin/env python3
"""
DOCX to PDF Converter with Bookmark Preservation for Linux/Windows
Fixed version detection and Windows bootstrap.ini issues
"""

import os
import sys
import subprocess
import shutil
import tempfile
import time
import uuid
from pathlib import Path
import logging
import platform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocxToPdfConverter:
    def __init__(self):
        self.temp_dir = None
        self.libreoffice_cmd = None
        self.supports_pdf_parameters = False
        self.system = platform.system().lower()
        self.active_profiles = []  # Track created profiles for cleanup
        self.setup_temp_directory()
        self.check_dependencies()
    
    def setup_temp_directory(self):
        """Tạo thư mục temp để xử lý"""
        self.temp_dir = tempfile.mkdtemp(prefix='docx_convert_')
        logger.info(f"Temp directory created: {self.temp_dir}")
    
    def find_libreoffice_executable(self):
        """Tìm executable LibreOffice trên các platform"""
        if self.system == 'windows':
            # Possible LibreOffice paths on Windows (updated for newer versions)
            possible_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                # Support for LibreOffice 24, 25 versions
                r"C:\Program Files\LibreOffice 25.2\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice 25.2\program\soffice.exe",
                r"C:\Program Files\LibreOffice 24.8\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice 24.8\program\soffice.exe",
                r"C:\Program Files\LibreOffice 7.0\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice 7.0\program\soffice.exe",
            ]
            
            # Check PATH first
            for cmd in ['soffice', 'libreoffice']:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, timeout=10)
                    if result.returncode == 0:
                        return cmd
                except:
                    pass
            
            # Check common installation paths
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            
            return None
            
        else:  # Linux/Mac
            # Check common commands
            commands = ['libreoffice', 'soffice']
            
            for cmd in commands:
                try:
                    result = subprocess.run([cmd, '--version'], capture_output=True, timeout=10)
                    if result.returncode == 0:
                        return cmd
                except:
                    continue
            
            return None
    
    def create_safe_profile_path(self):
        """
        Tạo safe profile path cho Windows và Linux
        Fix lỗi bootstrap.ini corrupt
        """
        # Generate unique profile name
        profile_id = f"lo_profile_{uuid.uuid4().hex[:8]}"
        
        if self.system == 'windows':
            # Windows: Use proper Windows path format
            profile_base = os.path.join(os.environ.get('TEMP', self.temp_dir), 'LibreOfficeProfiles')
            profile_dir = os.path.join(profile_base, profile_id)
            # Convert to proper Windows file URI
            profile_uri = f"file:///{profile_dir.replace(os.sep, '/')}"
        else:
            # Linux/Mac: Use /tmp
            profile_dir = f"/tmp/LibreOfficeProfiles/{profile_id}"
            profile_uri = f"file://{profile_dir}"
        
        # Create directory
        os.makedirs(profile_dir, exist_ok=True)
        
        # Track for cleanup
        self.active_profiles.append(profile_dir)
        
        logger.info(f"📁 Created profile: {profile_dir}")
        return profile_uri, profile_dir
    
    def create_libreoffice_profile_with_pdf_settings(self):
        """
        Tạo LibreOffice profile với PDF export settings được preset
        Workaround cho LibreOffice version cũ không support JSON parameters
        """
        profile_uri, profile_dir = self.create_safe_profile_path()
        
        # Tạo thư mục config
        config_dir = os.path.join(profile_dir, "user", "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Tạo file registrymodifications.xcu với PDF export settings
        registry_content = '''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <item oor:path="/org.openoffice.Office.Common/Filter/PDF/Export">
    <prop oor:name="ExportBookmarks" oor:op="fuse">
      <value>true</value>
    </prop>
    <prop oor:name="ExportBookmarksToNamedDestinations" oor:op="fuse">
      <value>true</value>
    </prop>
    <prop oor:name="UseTaggedPDF" oor:op="fuse">
      <value>true</value>
    </prop>
    <prop oor:name="ConvertOOoTargetToPDFTarget" oor:op="fuse">
      <value>true</value>
    </prop>
    <prop oor:name="ExportLinksRelativeFsys" oor:op="fuse">
      <value>false</value>
    </prop>
  </item>
</oor:items>
'''
        
        registry_file = os.path.join(config_dir, "registrymodifications.xcu")
        with open(registry_file, 'w', encoding='utf-8') as f:
            f.write(registry_content)
        
        logger.info(f"📁 Created LibreOffice profile with PDF settings: {profile_dir}")
        return profile_uri
    
    def check_libreoffice_version(self):
        """
        Improved version checking to handle LibreOffice 25.x and newer versions
        """
        try:
            result = subprocess.run(
                [self.libreoffice_cmd, '--version'], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                version_line = result.stdout.strip()
                logger.info(f"LibreOffice version detected: {version_line}")
                
                # More robust version parsing
                import re
                
                # Try different version patterns
                patterns = [
                    r'LibreOffice\s+(\d+)\.(\d+)\.(\d+)',  # Standard: LibreOffice 7.4.7
                    r'LibreOffice\s+(\d+)\.(\d+)',         # Short: LibreOffice 25.2
                    r'(\d+)\.(\d+)\.(\d+)',                # Just numbers: 7.4.7
                    r'(\d+)\.(\d+)',                       # Just major.minor: 25.2
                ]
                
                for pattern in patterns:
                    version_match = re.search(pattern, version_line)
                    if version_match:
                        groups = version_match.groups()
                        major = int(groups[0])
                        minor = int(groups[1]) if len(groups) > 1 else 0
                        
                        logger.info(f"Parsed version: {major}.{minor}")
                        
                        # Check if version supports PDF parameters
                        # LibreOffice 7.3+ or 25.x+ should support it
                        if major >= 25 or (major >= 7 and minor >= 3):
                            logger.info("✅ LibreOffice version supports PDF export parameters")
                            return True
                        else:
                            logger.warning(f"⚠️  LibreOffice {major}.{minor} may not support advanced PDF parameters")
                            return False
                
                # If we can't parse version, be conservative
                logger.warning("Cannot parse LibreOffice version, using profile workaround")
                return False
                
        except Exception as e:
            logger.warning(f"Cannot check LibreOffice version: {e}")
            return False
    
    def check_dependencies(self):
        """Kiểm tra LibreOffice có được cài đặt không"""
        self.libreoffice_cmd = self.find_libreoffice_executable()
        
        if not self.libreoffice_cmd:
            logger.error("❌ LibreOffice không được tìm thấy!")
            
            if self.system == 'windows':
                logger.error("Tải và cài đặt LibreOffice từ: https://www.libreoffice.org/download/download/")
                logger.error("Hoặc đảm bảo LibreOffice có trong PATH")
            else:
                logger.error("Cài đặt bằng: sudo apt-get install libreoffice")
            
            sys.exit(1)
        
        # Check version compatibility
        self.supports_pdf_parameters = self.check_libreoffice_version()
        
        try:
            result = subprocess.run(
                [self.libreoffice_cmd, '--version'], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                logger.info(f"✅ LibreOffice executable found: {self.libreoffice_cmd}")
                return True
            else:
                raise FileNotFoundError("LibreOffice not responding")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.error("❌ LibreOffice không hoạt động!")
            sys.exit(1)
    
    def validate_input_file(self, input_path):
        """Kiểm tra file input hợp lệ"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File không tồn tại: {input_path}")
        
        if not input_path.lower().endswith('.docx'):
            raise ValueError(f"File phải có định dạng .docx: {input_path}")
        
        # Kiểm tra file có thể đọc được
        try:
            with open(input_path, 'rb') as f:
                header = f.read(4)
                if header != b'PK\x03\x04':  # ZIP header (DOCX is ZIP)
                    raise ValueError(f"File DOCX không hợp lệ: {input_path}")
        except Exception as e:
            raise ValueError(f"Không thể đọc file: {e}")
        
        logger.info(f"✅ Input file validated: {input_path}")
    
    def prepare_output_path(self, output_path):
        """Chuẩn bị đường dẫn output"""
        output_path = Path(output_path)
        
        # Tạo thư mục parent nếu chưa có
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Đảm bảo extension là .pdf
        if output_path.suffix.lower() != '.pdf':
            output_path = output_path.with_suffix('.pdf')
        
        logger.info(f"Output path prepared: {output_path}")
        return str(output_path)
    
    def kill_existing_libreoffice_processes(self):
        """Kill any existing LibreOffice processes to avoid conflicts"""
        try:
            if self.system == 'windows':
                subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe'], 
                             capture_output=True, timeout=10)
                subprocess.run(['taskkill', '/F', '/IM', 'soffice.bin'], 
                             capture_output=True, timeout=10)
            else:
                subprocess.run(['pkill', '-f', 'soffice'], 
                             capture_output=True, timeout=10)
            
            # Wait a moment for processes to clean up
            time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Process cleanup: {e}")
    
    def convert_single_file(self, input_path, output_path, timeout=180):
        """
        Convert một file DOCX sang PDF với improved error handling
        """
        try:
            # Validate input
            self.validate_input_file(input_path)
            output_path = self.prepare_output_path(output_path)
            
            logger.info(f"🔄 Converting: {input_path} → {output_path}")
            
            # Kill any existing LibreOffice processes
            self.kill_existing_libreoffice_processes()
            
            # Tạo temp directory cho conversion này
            convert_temp = os.path.join(self.temp_dir, f"convert_{int(time.time())}_{uuid.uuid4().hex[:6]}")
            os.makedirs(convert_temp, exist_ok=True)
            
            # Prepare LibreOffice command
            if self.supports_pdf_parameters:
                # Modern LibreOffice: Use JSON parameters
                pdf_filter = 'pdf:writer_pdf_Export:{"ExportBookmarks":{"type":"boolean","value":"true"},"ExportBookmarksToNamedDestinations":{"type":"boolean","value":"true"},"UseTaggedPDF":{"type":"boolean","value":"true"}}'
                user_installation, _ = self.create_safe_profile_path()
                logger.info("🔖 Using advanced PDF export with bookmark preservation")
            else:
                # Older LibreOffice: Use custom profile
                pdf_filter = 'pdf:writer_pdf_Export'
                user_installation = self.create_libreoffice_profile_with_pdf_settings()
                logger.info("🔖 Using custom profile for bookmark preservation")
            
            # Build command
            cmd = [
                self.libreoffice_cmd,
                '--headless',
                '--invisible', 
                '--nodefault',
                '--nolockcheck',
                '--nologo',
                '--norestore',
                '--accept=socket,host=localhost,port=0;urp;StarOffice.ServiceManager',  # Add service manager
                f'-env:UserInstallation={user_installation}',
                '--convert-to', pdf_filter,
                '--outdir', convert_temp,
                os.path.abspath(input_path)
            ]
            
            logger.info("Running LibreOffice conversion...")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            start_time = time.time()
            
            # Run conversion with improved error handling
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=convert_temp
            )
            
            conversion_time = time.time() - start_time
            
            # Check result
            if result.returncode != 0:
                logger.error(f"LibreOffice error (code {result.returncode}):")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                
                # Try to provide helpful error messages
                if "bootstrap.ini" in result.stderr.lower():
                    logger.error("💡 Suggestion: Restart your computer and try again")
                    logger.error("💡 Or manually delete LibreOffice temp profiles")
                
                return False
            
            # Find the created PDF
            input_filename = os.path.basename(input_path)
            expected_pdf_name = os.path.splitext(input_filename)[0] + '.pdf'
            temp_pdf_path = os.path.join(convert_temp, expected_pdf_name)
            
            if not os.path.exists(temp_pdf_path):
                logger.error(f"PDF output not found: {temp_pdf_path}")
                logger.error(f"Files in temp dir: {os.listdir(convert_temp)}")
                return False
            
            # Move to final location
            shutil.move(temp_pdf_path, output_path)
            
            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Conversion successful in {conversion_time:.2f}s")
                logger.info(f"   Output: {output_path} ({file_size:,} bytes)")
                return True
            else:
                logger.error("Output file not created")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Conversion timeout after {timeout} seconds")
            # Kill LibreOffice processes on timeout
            self.kill_existing_libreoffice_processes()
            return False
        except Exception as e:
            logger.error(f"❌ Conversion error: {str(e)}")
            return False
        finally:
            # Cleanup temp files for this conversion
            if 'convert_temp' in locals() and os.path.exists(convert_temp):
                shutil.rmtree(convert_temp, ignore_errors=True)
    
    def verify_pdf_bookmarks(self, pdf_path, show_details=True):
        """
        Kiểm tra PDF có bookmark không với thông tin chi tiết
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if hasattr(reader, 'outline') and reader.outline:
                    bookmark_count = len(reader.outline)
                    logger.info(f"✅ Found {bookmark_count} bookmarks in PDF")
                    
                    if show_details and bookmark_count > 0:
                        # Print bookmark details
                        def print_bookmarks(bookmarks, level=0):
                            for i, bookmark in enumerate(bookmarks[:10]):  # Show max 10
                                indent = "  " * level
                                if hasattr(bookmark, 'title'):
                                    logger.info(f"{indent}{i+1}. {bookmark.title}")
                        
                        print_bookmarks(reader.outline)
                        if bookmark_count > 10:
                            logger.info(f"   ... and {bookmark_count - 10} more bookmarks")
                    
                    return True
                else:
                    logger.warning("❌ No bookmarks found in PDF")
                    logger.warning("   This may indicate:")
                    logger.warning("   - Original DOCX has no bookmarks/headings")
                    logger.warning("   - LibreOffice version issue")
                    logger.warning("   - Headings not using proper styles")
                    return False
                    
        except ImportError:
            logger.info("📝 Install PyPDF2 to verify bookmarks: pip install PyPDF2")
            return None
        except Exception as e:
            logger.warning(f"Cannot verify bookmarks: {e}")
            return None
    
    def batch_convert(self, input_dir, output_dir, pattern="*.docx"):
        """Convert batch files with improved error handling"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        docx_files = list(input_path.glob(pattern))
        
        if not docx_files:
            logger.warning(f"No DOCX files found in {input_dir}")
            return {"success": 0, "failed": 0, "files": []}
        
        logger.info(f"Found {len(docx_files)} DOCX files to convert")
        
        results = {"success": 0, "failed": 0, "files": []}
        
        for i, docx_file in enumerate(docx_files, 1):
            pdf_filename = docx_file.stem + '.pdf'
            pdf_output = output_path / pdf_filename
            
            logger.info(f"[{i}/{len(docx_files)}] Processing: {docx_file.name}")
            
            success = self.convert_single_file(str(docx_file), str(pdf_output))
            
            file_result = {
                "input": str(docx_file),
                "output": str(pdf_output),
                "success": success
            }
            
            if success:
                results["success"] += 1
                self.verify_pdf_bookmarks(str(pdf_output), show_details=False)
            else:
                results["failed"] += 1
            
            results["files"].append(file_result)
        
        # Summary
        total = results["success"] + results["failed"]
        logger.info(f"\n📊 Batch conversion completed:")
        logger.info(f"   ✅ Success: {results['success']}/{total}")
        logger.info(f"   ❌ Failed:  {results['failed']}/{total}")
        
        return results
    
    def cleanup(self):
        """Enhanced cleanup"""
        # Cleanup temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info(f"Temp directory cleaned up: {self.temp_dir}")
        
        # Cleanup active profiles
        for profile_dir in self.active_profiles:
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir, ignore_errors=True)
                logger.debug(f"Profile cleaned up: {profile_dir}")
        
        # Kill any remaining LibreOffice processes
        self.kill_existing_libreoffice_processes()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

# Convenience functions
def convert_docx_to_pdf(input_path, output_path):
    """Simple conversion function"""
    with DocxToPdfConverter() as converter:
        return converter.convert_single_file(input_path, output_path)

def batch_convert_docx_to_pdf(input_dir, output_dir):
    """Simple batch conversion function"""
    with DocxToPdfConverter() as converter:
        return converter.batch_convert(input_dir, output_dir)

# Main execution
if __name__ == "__main__":
    print("🚀 DOCX to PDF Converter with Bookmark Preservation (Fixed)")
    print("=" * 60)
    
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        print(f"Converting: {input_file} → {output_file}")
        
        success = convert_docx_to_pdf(input_file, output_file)
        
        if success:
            print("✅ Conversion completed successfully!")
            
            with DocxToPdfConverter() as converter:
                converter.verify_pdf_bookmarks(output_file, show_details=True)
        else:
            print("❌ Conversion failed!")
            sys.exit(1)
    
    else:
        print("Usage:")
        print("  python converter.py input.docx output.pdf")
        print("\nOr use in code:")
        print("  from converter import convert_docx_to_pdf")
        print("  convert_docx_to_pdf('input.docx', 'output.pdf')")
        
        # Test if available
        test_input = "test.docx"
        if os.path.exists(test_input):
            print(f"\n🧪 Testing with {test_input}...")
            with DocxToPdfConverter() as converter:
                success = converter.convert_single_file(test_input, "test.pdf")
                if success:
                    converter.verify_pdf_bookmarks("test.pdf", show_details=True)