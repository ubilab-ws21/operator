.PHONY: build

ifndef VERSION 
$(error Please use 'make VERSION=x.x-x')
endif 
TMP_DIR = ue-operator_$(VERSION)

build:
	cp -r ue-operator $(TMP_DIR)
	# example copying the webinterface
	mkdir -p $(TMP_DIR)/var/www/html/
	cp -r ../webinterface/* $(TMP_DIR)/var/www/html/
	# Add custom copy commands here
	sudo chown -R root:root $(TMP_DIR)/etc
	sudo chown -R root:root $(TMP_DIR)/usr
	sudo chown -R root:root $(TMP_DIR)/var
	sudo chmod +x $(TMP_DIR)/usr/bin/ue-operator
	sed -i 's/%VERSION%/$(VERSION)/g' $(TMP_DIR)/DEBIAN/control 
	dpkg-deb --build $(TMP_DIR)
	sudo rm -rf $(TMP_DIR)
