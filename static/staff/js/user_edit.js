/**
 * User Edit Page JavaScript
 * Handles college dropdown functionality and form interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initCollegeDropdown();
});

/**
 * Initialize college dropdown functionality
 */
function initCollegeDropdown() {
    const provinceField = document.querySelector('select[name="province"]');
    const collegeTypeField = document.querySelector('select[name="college_type"]');
    const collegeNameField = document.querySelector('select[name="college_name"]');
    
    if (provinceField && collegeTypeField && collegeNameField) {
        // Add event listeners
        provinceField.addEventListener('change', updateCollegeChoices);
        collegeTypeField.addEventListener('change', updateCollegeChoices);
        
        // Initialize on page load with current values
        updateCollegeChoices();
    }
}

/**
 * Update college choices based on province and college type selection
 */
function updateCollegeChoices() {
    const provinceField = document.querySelector('select[name="province"]');
    const collegeTypeField = document.querySelector('select[name="college_type"]');
    const collegeNameField = document.querySelector('select[name="college_name"]');
    
    if (!provinceField || !collegeTypeField || !collegeNameField) return;
    
    const province = provinceField.value;
    const collegeType = collegeTypeField.value;
    const currentCollegeName = collegeNameField.value; // Save current selection
    
    // Medical colleges data (matching the backend)
    const medicalColleges = {
        "Punjab": {
            "Public": [
                "Allama Iqbal Medical College (Lahore)",
                "Ameer-ud-Din (PGMI) Medical College (Lahore)",
                "Army Medical College (Rawalpindi)",
                "D.G. Khan Medical College (Dera Ghazi Khan)",
                "Fatima Jinnah Medical College (Lahore)",
                "Services Institute of Medical Sciences (Lahore)",
                "Gujranwala Medical College",
                "Khawaja Muhammad Safdar MC (Sialkot)",
                "King Edward Medical University (Lahore)",
                "Nawaz Sharif Medical College (Gujrat)",
                "Nishtar Medical College (Multan)",
                "Punjab Medical College (Faisalabad)",
                "Quaid‑e‑Azam Medical College (Bahawalpur)",
                "Rawalpindi Medical College (Rawalpindi)",
                "Sahiwal Medical College",
                "Sargodha Medical College",
                "Shaikh Khalifa Bin Zayed MC (Lahore)",
                "Sheikh Zayed Medical College (Rahim Yar Khan)",
                "Narowal Medical College"
            ],
            "Private": [
                "FMH College of Medicine & Dentistry (Lahore)",
                "Lahore Medical & Dental College",
                "University College of Medicine & Dentistry (Lahore)",
                "Al Aleem Medical College",
                "Rahbar Medical College",
                "Rashid Latif Medical College",
                "Azra Naheed Medical College",
                "Pak Red Crescent Medical College",
                "Sharif Medical & Dental College",
                "Continental Medical College",
                "Akhtar Saeed Medical College",
                "CMH Lahore Medical & Dental College",
                "Shalamar Medical & Dental College",
                "Avicenna Medical College",
                "Abwa Medical College",
                "Independent Medical College",
                "Aziz Fatima Medical College",
                "Multan Medical & Dental College",
                "Bakhtawar Amin Medical & Dental College",
                "Central Park Medical College",
                "CIMS Multan",
                "HITEC Institute of Medical Sciences",
                "Hashmat Medical & Dental College",
                "Shahida Islam Medical College",
                "Wah Medical College",
                "Sahara Medical College",
                "CMH Kharian Medical College",
                "M. Islam Medical College",
                "Islam Medical College",
                "Fazaia Medical College",
                "Rai Medical College",
                "Margalla Institute of Health Sciences",
                "Mohammad Dental College",
                "Islamabad Medical & Dental College",
                "Yusra Medical & Dental College"
            ]
        },
        "Sindh": {
            "Public": [
                "Dow Medical College",
                "Dow International Medical College",
                "Karachi Medical & Dental College",
                "Chandka Medical College (Larkana)",
                "Ghulam Muhammad Mahar Medical College (Sukkur)",
                "Liaquat University of Medical & Health Sciences (Jamshoro)",
                "Peoples UMHS for Women (Nawabshah)",
                "Shaheed Mohtarma Benazir Bhutto MC (Lyari, Karachi)",
                "Jinnah Sindh Medical University",
                "Khairpur Medical College",
                "Bilawal Medical College (Hyderabad)"
            ],
            "Private": [
                "Aga Khan University",
                "Baqai Medical College",
                "Hamdard College of Medicine & Dentistry",
                "Jinnah Medical & Dental College",
                "Sir Syed College of Medical Sciences",
                "Ziauddin Medical College",
                "Liaquat National Medical College",
                "Bahria University Medical College",
                "Karachi Institute of Medical Sciences",
                "Al‑Tibri Medical College",
                "United Medical & Dental College",
                "Indus Medical College (Tando Muhammad Khan)",
                "Isra University Hyderabad",
                "Muhammad Medical College (Mirpurkhas)",
                "Suleman Roshan Medical College (Tando Adam)",
                "Fazaia Ruth Pfau Medical College (Karachi)"
            ]
        },
        "Khyber Pakhtunkhwa": {
            "Public": [
                "Khyber Medical College (Peshawar)",
                "Khyber Girls Medical College",
                "Ayub Medical College (Abbottabad)",
                "Saidu Medical College (Swat)",
                "Gomal Medical College (D.I. Khan)",
                "KMU Institute of Medical Sciences (Kohat)",
                "Bannu Medical College",
                "Bacha Khan Medical College (Mardan)",
                "Gajju Khan Medical College (Swabi)",
                "Nowshera Medical College"
            ],
            "Private": [
                "Abbottabad International Medical College",
                "Al‑Razi Medical College",
                "Frontier Medical College (Abbottabad)",
                "Kabir Medical College (Peshawar)",
                "Northwest School of Medicine",
                "Pak International Medical College",
                "Peshawar Medical College",
                "Rehman Medical College",
                "Women Medical & Dental College (Abbottabad)",
                "Swat Medical College",
                "Jinnah Medical College (Peshawar)"
            ]
        },
        "Balochistan": {
            "Public": [
                "Bolan Medical College (Quetta)",
                "Loralai Medical College",
                "Makran Medical College (Turbat)",
                "Jhalawan Medical College (Khuzdar)"
            ],
            "Private": [
                "Quetta Institute of Medical Sciences (Quetta)"
            ]
        },
        "Azad Jammu & Kashmir": {
            "Public": [
                "Azad Jammu & Kashmir Medical College (Muzaffarabad)",
                "Mohtarma Benazir Bhutto Shaheed Medical College (Mirpur)",
                "Poonch Medical College (Rawalakot)"
            ],
            "Private": [
                "Mohiuddin Islamic Medical College (Mirpur)"
            ]
        }
    };
    
    // Clear college name field
    collegeNameField.innerHTML = '<option value="">Select medical college</option>';
    
    // If both province and college type are selected, populate colleges
    if (province && collegeType && medicalColleges[province] && medicalColleges[province][collegeType]) {
        const colleges = medicalColleges[province][collegeType];
        colleges.forEach(college => {
            const option = document.createElement('option');
            option.value = college;
            option.textContent = college;
            
            // Restore selection if it matches
            if (college === currentCollegeName) {
                option.selected = true;
            }
            
            collegeNameField.appendChild(option);
        });
        collegeNameField.disabled = false;
    } else {
        // Set placeholder based on what's missing
        if (!province && !collegeType) {
            collegeNameField.innerHTML = '<option value="">Select province and type first</option>';
        } else if (!province) {
            collegeNameField.innerHTML = '<option value="">Select province first</option>';
        } else if (!collegeType) {
            collegeNameField.innerHTML = '<option value="">Select college type first</option>';
        }
        collegeNameField.disabled = true;
    }
}

/**
 * Show notification to user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}
