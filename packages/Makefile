.PHONY: build

ifndef VERSION 
$(error Please use 'make VERSION=x.x-x')
endif 
TMP_DIR = ue-operator_$(VERSION)

build:
    # creating work directory
	cp -r ue-operator $(TMP_DIR)
	# copying the webinterface
	mkdir -p $(TMP_DIR)/var/www/html/
	cp -r ../webinterface/* $(TMP_DIR)/var/www/html/
	# copying the game logic
	mkdir -p $(TMP_DIR)/opt/ue-operator/logic
	cp -r ../logic/* $(TMP_DIR)/opt/ue-operator/logic
	# copying binaries
	mkdir -p $(TMP_DIR)/usr/bin/
	cp -r ../bin/* $(TMP_DIR)/usr/bin/
	# changing directory and binary execution permissions
	sudo chown -R root:root $(TMP_DIR)/etc
	sudo chown -R root:root $(TMP_DIR)/usr
	sudo chown -R root:root $(TMP_DIR)/var
	sudo chmod +x $(TMP_DIR)/usr/bin/ue-operator
	sudo chmod +x $(TMP_DIR)/usr/bin/ue-camera
	# Write version and build
	sed -i 's/%VERSION%/$(VERSION)/g' $(TMP_DIR)/DEBIAN/control 
	dpkg-deb --build $(TMP_DIR)
	sudo rm -rf $(TMP_DIR)
